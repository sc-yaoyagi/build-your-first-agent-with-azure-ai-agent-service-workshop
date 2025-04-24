"""Main entry point for the lab project."""
import asyncio
import logging

from lab1 import Lab1
from lab2 import Lab2
from lab3 import Lab3
from lab4 import Lab4
from lab5 import Lab5
from terminal_colors import TerminalColors as tc

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Choose your lab:
lab = Lab1()
# lab = Lab2()
# lab = Lab3()
# lab = Lab4()
# lab = Lab5()


async def main() -> None:
    # Delegate initialization into the base class
    agent, thread = await lab.initialize()
    if not agent or not thread:
        print(f"{tc.BG_BRIGHT_RED}Failed to initialize Lab.{tc.RESET}")
        return

    while True:
        prompt = input(
            f"\n\n{tc.GREEN}Enter query (or exit/save): {tc.RESET}").strip()
        if not prompt:
            continue
        cmd = prompt.lower()
        if cmd in {"exit", "save"}:
            break
        await lab.post_message(thread_id=thread.id, content=prompt, agent=agent, thread=thread)

    if cmd == "save":
        print("Agent retained for further experimentation in Azure AI Foundry.")
        print(
            f"Go to https://ai.azure.com → your project → Playgrounds → select agent ID {agent.id}")
    else:
        await lab.cleanup(agent, thread)
        print("Cleaned up agent resources.")


if __name__ == "__main__":
    asyncio.run(main())
