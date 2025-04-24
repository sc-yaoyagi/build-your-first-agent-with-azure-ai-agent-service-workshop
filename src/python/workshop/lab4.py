# File: lab4.py
from azure.ai.projects.models import CodeInterpreterTool, FileSearchTool

from lab_base import LabBase

INSTRUCTIONS_FILE = "instructions/code_interpreter_multilingual.txt"
TENTS_DATA_SHEET_FILE = "datasheet/contoso-tents-datasheet.pdf"
FONTS_ZIP = "fonts/fonts.zip"


class Lab4(LabBase):
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

        self.font_file_info = await self.utilities.upload_file(
            self.project_client,
            self.utilities.shared_files_path / FONTS_ZIP
        )
        code_interpreter.add_file(file_id=self.font_file_info.id)
        
        return self.font_file_info
