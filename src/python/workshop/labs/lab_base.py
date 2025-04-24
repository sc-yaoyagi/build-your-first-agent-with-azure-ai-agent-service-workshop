# File: lab_base.py
import logging
import os
from abc import ABC, abstractmethod

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import Agent, AgentThread, AsyncFunctionTool, AsyncToolSet
from azure.identity import DefaultAzureCredential

from sales_data import SalesData
from stream_event_handler import StreamEventHandler
from terminal_colors import TerminalColors as tc
from utilities import Utilities

logger = logging.getLogger(__name__)

AGENT_NAME = "Contoso Sales Agent"
API_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")
PROJECT_CONNECTION_STRING = os.environ["PROJECT_CONNECTION_STRING"]
MAX_COMPLETION_TOKENS = 10240
MAX_PROMPT_TOKENS = 20480
TEMPERATURE = 0.1
TOP_P = 0.1


class LabBase(ABC):
    """Abstract base class for labs defining tool setup and initialization."""

    def __init__(self, instructions_file: str) -> None:
        self.instructions = instructions_file
        self.font_file_info = None
        self.agent = None
        self.thread = None
        self.toolset = AsyncToolSet()
        self.utilities = Utilities()
        self.sales_data = SalesData(self.utilities)
        self.functions = AsyncFunctionTool({self.sales_data.async_fetch_sales_data_using_sqlite_query})
        self.project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=PROJECT_CONNECTION_STRING,
        )

    @abstractmethod
    async def add_agent_tools(self) -> None:
        """Configure the shared toolset for this lab."""
        ...

    async def post_message(self, thread_id: str, content: str, agent: Agent, thread: AgentThread) -> None:
        try:
            await self.project_client.agents.create_message(thread_id=thread_id, role="user", content=content)
            stream = await self.project_client.agents.create_stream(
                thread_id=thread.id,
                agent_id=agent.id,
                event_handler=StreamEventHandler(
                    functions=self.functions, project_client=self.project_client, utilities=self.utilities
                ),
                max_completion_tokens=MAX_COMPLETION_TOKENS,
                max_prompt_tokens=MAX_PROMPT_TOKENS,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                instructions=agent.instructions,
            )
            async with stream as s:
                await s.until_done()
        except Exception as e:
            self.utilities.log_msg_purple(f"Error posting message: {e}")

    async def initialize(self) -> tuple[Agent, AgentThread]:
        """Common initialize: add tools, load instructions, create agent & thread."""
        if not self.instructions:
            return None, None

        # 1) let subclass add its tools
        font_info = await self.add_agent_tools()

        # 2) connect sales_data and get schema
        await self.sales_data.connect()
        schema = await self.sales_data.get_database_info()

        try:
            # 3) load & template instructions
            instructions = self.utilities.load_instructions(self.instructions)
            instructions = instructions.replace("{database_schema_string}", schema)
            if font_info:
                instructions = instructions.replace("{font_file_id}", font_info.id)

            # 4) create agent
            self.agent = await self.project_client.agents.create_agent(
                model=API_DEPLOYMENT_NAME,
                name=AGENT_NAME,
                instructions=instructions,
                toolset=self.toolset,
                temperature=TEMPERATURE,
                headers={"x-ms-enable-preview": "true"},
            )
            # 5) create thread
            self.thread = await self.project_client.agents.create_thread()
            return self.agent, self.thread

        except Exception as e:
            logger.error("Initialization error: %s", e)
            print(f"{tc.BG_BRIGHT_RED}Initialization failed: {e}{tc.RESET}")
            return None, None

    async def cleanup(self, agent: Agent, thread: AgentThread) -> None:
        await self.project_client.agents.delete_thread(thread.id)
        await self.project_client.agents.delete_agent(agent.id)
        await self.sales_data.close()
