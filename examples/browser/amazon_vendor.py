import asyncio
import os
import sys
from dotenv import load_dotenv
from typing import cast, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from browser_use import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use.browser.browser import Browser
from browser_use.llm import ChatOpenAI

load_dotenv()

AMAZON_URL = os.getenv('AMAZON_URL') 
AMAZON_EMAIL = os.getenv('AMAZON_EMAIL') 
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD') 



browser = Browser()

task_prompt = f"""
You are an autonomous AI agent. Your task is to log into Amazon Vendor Central, verify with OTP via Outlook, and download the Excel invoice template for a single Purchase Order (PO).

### Step 1: Login to Amazon Vendor Central
1. Open the following URL: **{AMAZON_URL}**
2. Wait for the page to load fully.
3. Enter this email:harry@sanfe.in , after entering email click continue to move to next page and then enter password

4. Enter the password  : Sanfe@2025#Red.
5. Click the “Sign In” button.
6. Wait for the OTP screen to appear.

7. wait for user to enter otp and navigate to the main dashboard after submitting otp.

### Step 3: Navigate to the Invoices Section
13. Click the hamburger menu (☰) in the top-left corner.
14. Click or hover  on “Payments”.
15. Then click “Invoices”.

### Step 4: Create Invoice for a Single PO
16. Click the yellow “Create Invoice” button.
17. On the Purchase Order page, **select only the first PO** by checking its box (do not select all).
18. Scroll down and click the “Create Invoice” button.

### Step 5: Download the Excel Template
19. On the invoice creation screen, scroll to **“Update line items using Excel”**.
20. Click the **“Download Excel”** button.
21. Wait for the status indicator (next to the button) to show “Success” or “Download completed”.

### Step 6: Finish
22. Once the Excel is downloaded, you have to start from step 4 again and download rest of purchase until all alre downloaded  as in one step one is only downloaded.

Important rules:
- Do not select multiple POs.
- Do not click the download button multiple times.
- Be patient with UI transitions.
- Mimic human-like, slow, and accurate interactions.
"""

# Run the agent
async def run_download():
    llm = cast(Any, ChatOpenAI(model="gpt-4o", temperature=1.0))

    agent = Agent(
        task=task_prompt,
        llm=llm,
     
        max_actions_per_step=8,
        use_vision=True,
        browser=browser
    )

    await agent.run(max_steps=50)
    await browser.close()


if __name__ == '__main__':
    asyncio.run(run_download())
