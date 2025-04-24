# File: lab3.py
from azure.ai.projects.models import CodeInterpreterTool, FileSearchTool

from labs.lab_base import LabBase

INSTRUCTIONS_FILE = "instructions/code_interpreter.txt"
TENTS_DATA_SHEET_FILE = "datasheet/contoso-tents-datasheet.pdf"


class Lab3(LabBase):
    def __init__(self) -> None:
        super().__init__(INSTRUCTIONS_FILE)

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
