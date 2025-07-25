import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from browser_use import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use.llm import ChatOpenAI

async def main():
    browser_session = BrowserSession(
        browser_profile=BrowserProfile(
            keep_alive=True,
            user_data_dir=None,
            headless=False,
        )
    )
    await browser_session.start()

    llm = ChatOpenAI(model="o4-mini",temperature=1.0)
    
    task1 = (
        "Go to https://www.flipkart.com/. "
        "Search for 'Samsung S24' whose price is greater than 50000,and pick any 1 product then do next task "
        "Extract the product's title, price, and product link as JSON."
    )
    task2 = (
        "Take the product link from agent1's JSON output. "
        "go to product link you extracted as json "
        "keep the selection as buy wihtout exchange only "
        "below the product image there will be two options add to cart and buy now you have to click on 'ADD TO CART' "
        "after clicking confirm that it is added to cart"
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