# File: lab1.py
from labs.lab_base import LabBase

INSTRUCTIONS_FILE = "instructions/function_calling.txt"


class Lab1(LabBase):
    def __init__(self) -> None:
        """Initialize the Lab1 class."""
        super().__init__(INSTRUCTIONS_FILE)

    async def add_agent_tools(self) -> None:
        """Add tools to the agent's toolset."""
        self.toolset.add(self.functions)
