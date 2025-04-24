# File: lab5.py
import os

from azure.ai.projects.models import BingGroundingTool, CodeInterpreterTool, FileSearchTool

from labs.lab_base import LabBase

INSTRUCTIONS_FILE = "instructions/bing_grounding.txt"
BING_CONNECTION_NAME = os.getenv("BING_CONNECTION_NAME")
TENTS_DATA_SHEET_FILE = "datasheet/contoso-tents-datasheet.pdf"


class Lab5(LabBase):
    def __init__(self, instructions_file: str) -> None:
        super().__init__(instructions_file)

    async def add_agent_tools(self) -> None:
        self.toolset.add(self.functions)

        vector_store = await self.utilities.create_vector_store(
            self.project_client,
            files=[TENTS_DATA_SHEET_FILE],
            vector_store_name="Contoso Product Information Vector Store",
        )
        file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])
        self.toolset.add(file_search_tool)

        code_interpreter = CodeInterpreterTool()
        self.toolset.add(code_interpreter)

        bing_conn = await self.project_client.connections.get(connection_name=BING_CONNECTION_NAME)
        bing_tool = BingGroundingTool(connection_id=bing_conn.id)
        self.toolset.add(bing_tool)
        return self.font_file_info
