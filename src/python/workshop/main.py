"""Main entry point for the workshop."""

import asyncio
import logging

from labs.lab1 import Lab1
from labs.lab2 import Lab2
from labs.lab3 import Lab3
from labs.lab4 import Lab4
from labs.lab5 import Lab5
from terminal_colors import TerminalColors as tc

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Set your lab:
LAB_NUMBER = 1

lab_classes = {
    1: Lab1,
    2: Lab2,
    3: Lab3,
    4: Lab4,
    5: Lab5,
}


async def workshop() -> None:
    """Main function to run the lab."""

    lab = lab_classes.get(LAB_NUMBER)()
    if lab is None:
        raise ValueError(f"Invalid LAB_NUMBER: {LAB_NUMBER}")

    async with lab.project_client:
        agent, thread = await lab.initialize()
        
        if not agent or not thread:
            print(f"{tc.BG_BRIGHT_RED}Failed to initialize Lab.{tc.RESET}")
            return

        while True:
            prompt = input(f"\n\n{tc.GREEN}Enter query (or exit/save): {tc.RESET}").strip()
            if not prompt:
                continue
            cmd = prompt.lower()
            if cmd in {"exit", "save"}:
                break
            await lab.post_message(thread_id=thread.id, content=prompt, agent=agent, thread=thread)

        if cmd == "save":
            print("Agent retained for further experimentation in Azure AI Foundry.")
            print(f"Go to https://ai.azure.com → your project → Playgrounds → select agent ID {agent.id}")
        else:
            await lab.cleanup(agent, thread)
            print("Cleaned up agent resources.")


if __name__ == "__main__":
    asyncio.run(workshop())
