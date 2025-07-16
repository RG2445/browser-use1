import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from browser_use import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use.llm import ChatGroq

async def main():
    browser_session = BrowserSession(
        browser_profile=BrowserProfile(
            keep_alive=True,
            user_data_dir=None,
            headless=False,
        )
    )
    await browser_session.start()

    llm = ChatGroq(model='meta-llama/llama-4-maverick-17b-128e-instruct')

    # Prompt engineering for Amazon tasks
    task1 = (
        "Go to https://www.amazon.in/. "
        "Search for 'Samsung S24'. "
        "Extract the  product's title and check the price if the price is greater than 50000 then only proceed forward and extract , price, and product link as JSON."
    )
    task2 = (
        "Take the product link from agent1's JSON output. "
        "Visit the product page. "
        "Add the product to the cart. "
        "Confirm that the item has been added."
    )

    agent1 = Agent(
        task=task1,
        browser_session=browser_session,
        llm=llm,
        agent_name="AmazonSearcher"
    )
    agent2 = Agent(
        task=task2,
        browser_session=browser_session,
        llm=llm,
        agent_name="CartAdder"
    )

    await asyncio.gather(
        agent1.run(),
        agent2.run()
    )

    await browser_session.kill()

asyncio.run(main())