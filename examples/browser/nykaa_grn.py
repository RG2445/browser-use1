import asyncio
import os
 
from dotenv import load_dotenv
from browser_use import Agent, Browser
from browser_use.browser.profile import BrowserProfile
from browser_use.llm import ChatOpenAI
 
load_dotenv()
 
NYKAA_URL = os.getenv('nykaa_url')
NYKAA_EMAIL = os.getenv('nykaa_email')

 
CURRENT_TIMESTAMP = "2025-07-29 12:30:00"
USER_LOGIN = "RG2445"
CURRENT_DATE = "29 JULY 2025"
 
browser_profile = BrowserProfile(
    downloads_path=r"/Users/rishit/Desktop"
)
browser = Browser(browser_profile=browser_profile)
llm = ChatOpenAI(model='gpt-4o', temperature=0)
 
 
task_prompt = """
You are an automation bot for downloading nykaa GRNS. Follow these exact steps:

INITIAL LOGIN (Execute Once):
1. Navigate to Nykaa vendor portal :{nykaa_url}
2. Enter email credentials: {nykaa_email}
3. Click Login button "Login to Nykaa"
4. WAIT for human OTP input and complete verification until dashboard is loaded
5. Dismiss any popups if they appear
6. on the dashboard, click the hamburger icon (sidebar menu) to open it .
7. Ensure you are on the "Good Received Notes" section of the sidebar menu.
8. Click on "Download" button in the sidebar menu.
9. once the box opens , the date range will appear .
10. there will be two calendar icons, click on the left one.
11.once calendar appears, click '>' to move to february month once .then click 1st date of february month.
12. Click on the right calendar icon to set the end date.
13. once calendar appears, click '<' to move to june month once .then click 15th date of june month.
12. then after setting date , there will be two download buttons
13.one for "GRN REPORT" and other for "GRN SKU-WISE REPORT".firs click on "GRN REPORT" button
14. Wait for the download to complete.
15. Now click on the "GRN SKU-WISE REPORT" button.
16. Wait for the download to complete.

now your task is completed and you can close the browser





CRITICAL RULES:

-you don't have to click any other unneceaary button on page just follo my instruction as i want you to execute the task

- Always wait for page loads between URL changes


-FOLLOW STEPS IN PROPER ORDER AS THE PROMPT IS GIVEN .FOLLOW ALL THE STEPS LINE BY LINE DO ONLY WHAT YOU ARE ASKED TO DO .YOU CANT DO ANYTHING WRONG .YOU ARE MY SLAVE
-At any step you should not click on any other button in sidebar menu or any other button on page except the ones mentioned in the steps

-you should not hallucinate or make assumptions about the task, follow the steps exactly as given THIS IS VERY IMPORTANT
- Dont click unnecessary  on page except the ones mentioned in the steps


"""
 
 

 
async def run_download():
    formatted_task = task_prompt.format(
        timestamp=CURRENT_TIMESTAMP,
        user=USER_LOGIN,
        nykaa_url=NYKAA_URL,
        nykaa_email=NYKAA_EMAIL,
        )
 
    agent = Agent(
        task=formatted_task,
        llm=llm,
        max_actions_per_step=8,
        use_vision=True,
        browser=browser
    )
 
    await agent.run(max_steps=100)
 
    await browser.close()
 
if __name__ == '__main__':
    asyncio.run(run_download())