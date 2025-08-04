import asyncio
import os
 
from dotenv import load_dotenv
from browser_use import Agent, Browser
from browser_use.browser.profile import BrowserProfile
from browser_use.llm import ChatOpenAI
 
load_dotenv()
 
ZEPTO_URL = os.getenv('zepto_url')
ZEPTO_EMAIL = os.getenv('zepto_email')
ZEPTO_PASSWORD = os.getenv('zepto_password')
 
CURRENT_TIMESTAMP = "2025-07-19 12:30:00"
USER_LOGIN = "RG2445"
CURRENT_DATE = "19 JULY 2025"
 
browser_profile = BrowserProfile(
    downloads_path=r"C:\Users\RishitGupta\Desktop\browser-use1"
)
browser = Browser(browser_profile=browser_profile)
llm = ChatOpenAI(model='gpt-4o', temperature=0)
 
 
task_prompt = """
You are an automation bot for downloading Zepto vendor invoices. Follow these exact steps:

INITIAL LOGIN (Execute Once):
1. Navigate to Zepto vendor portal
2. Enter email credentials: {zepto_email}
3. Enter password: {zepto_password}
4. Click Login button
5. WAIT for human OTP input and complete verification until dashboard is loaded
6. Dismiss any popups that appear

MONTH 1 - MAY 2025 (May 1 to May 31): 
1. sidebar menu is already opened (hamburger icon).
2. See for the  Payments section  there click on "Payments". A dropdown will appear
3. In dropdown menu, click "Invoices" 
4. Wait for invoices page to load completely.Near Top right corner you will see a date  button with a calendar icon on the left of Learning Hub button .the current date would set to july month ou hav to change it to May month
5.  your first priority is to change the date. take this action very seriously , click calendar icon .  Click start date and change it  to month of May
6. Set start date: May 1, 2025.
7. Check end date will be auto set to May 31, 2025. just check dont click any other button and now go to next step.
8. Click Apply  button
9. Wait for table to refresh with filtered data
10. Click Download button (this downloads page 0)
11. Navigate to URL: https://brands.zepto.co.in/vendor/payments/invoices?invoiceStartDate=2025-05-01T00%3A00%3A00.000Z&invoiceEndDate=2025-05-31T23%3A59%3A59.999Z&pageNumber=1
12.Now load this URL in browser.
13. Click Download button
14. Change URL pageNumber to 2, press Enter, click Download
15. Continue incrementing pageNumber (3,4,5...) until you see "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied." message in center of page

MONTH 2 - JUNE 2025 (June 1 to June 30):
1. Open date picker again .CLick a button similar to '>' to move to june month
2. Set start date: June 1, 2025
3.CHECK THAT END IS AUTO set for one month later like 1 july 2025
4. Click Apply  button.now dont click on date again until you see that all pages are downloaded and on screen you see "No Data found Sorry we couldn't find the data you were looking for." message
5. Wait for table to refresh
6. Click Download button ( this downloads    page 0)
7. Navigate to URL: https://brands.zepto.co.in/vendor/payments/invoices?invoiceStartDate=2025-06-01T00%3A00%3A00.000Z&invoiceEndDate=2025-06-30T23%3A59%3A59.999Z&pageNumber=1
8. Now load this URL in browser.
9. Click Download button
10. Change URL pageNumber to 2, press Enter, click Download
11. Continue incrementing pageNumber (3,4,5...) until you see "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied." message in center of page

MONTH 3 - JULY 2025:
1. Open date picker again click '>' to move to July month
2. Set start date: July 2, 2025
3. Check end date is auto set to 24 July 2025
4. Click Apply button
5. Wait for table to refresh
6. Click Download button (page 0)
7. Navigate to URL: https://brands.zepto.co.in/vendor/payments/invoices?invoiceStartDate=2025-07-01T00%3A00%3A00.000Z&invoiceEndDate=2025-07-24T23%3A59%3A59.999Z&pageNumber=1
8. Now load this URL in browser.
9. Click Download button
10. Change URL pageNumber to 2, press Enter, click Download(this downoloads page number 3 and so on)
11. Continue incrementing pageNumber (3,4,5...) until you see "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied." message in center of page

After completing all months, ensure the following:
- All pages for May, June, and July 2025 are downloaded without overlapping dates
- No unnecessary buttons are clicked except those specified in the steps
- Wait for page loads between URL changes
- Do not repeat dates across different months.



CRITICAL RULES:
- Complete ALL pages for one month before moving to next month
-you don't have to click any other unneceaary button on page just follo my instruction as i want you to execute the task
- Never overlap date ranges between months
- Always wait for page loads between URL changes
- Stop pagination when "No Data found" message appears
- Do not repeat dates across different months
-FOLLOW STEPS IN PROPER ORDER AS THE PROMPT IS GIVEN .FOLLOW ALL THE STEPS LINE BY LINE DO ONLY WHAT YOU ARE ASKED TO DO .YOU CANT DO ANYTHING WRONG .YOU ARE MY SLAVE
-At any step you should not click on any other button in sidebar menu or any other button on page except the ones mentioned in the steps
- URL pageNumber starts from 1 (page 0 is downloaded first without pageNumber parameter)
-you should not hallucinate or make assumptions about the task, follow the steps exactly as given THIS IS VERY IMPORTANT
- Dont click unnecessary buttons like "Learning Hub" or any other button on page except the ones mentioned in the steps

COMPLETION CHECK:
✓ May 2025: Downloaded pages 0,1,2,3... until No Data found
✓ June 2025: Downloaded pages 0,1,2,3... until No Data found  
✓ July 2025: Downloaded pages 0,1,2,3... until No Data found
"""
 
 

 
async def run_download():
    formatted_task = task_prompt.format(
        timestamp=CURRENT_TIMESTAMP,
        user=USER_LOGIN,
        zepto_url=ZEPTO_URL,
        zepto_email=ZEPTO_EMAIL,
        zepto_password=ZEPTO_PASSWORD
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