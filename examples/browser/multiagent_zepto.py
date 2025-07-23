import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()


from browser_use import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser.session import BrowserSession
from browser_use.llm import ChatOpenAI

ZEPTO_URL = os.getenv('zepto_url')
ZEPTO_EMAIL = os.getenv('zepto_email')
ZEPTO_PASSWORD = os.getenv('zepto_password')



async def main():
	browser_session = BrowserSession(
		browser_profile=BrowserProfile(
			downloads_path=r"C:\Users\RishitGupta\Desktop\browser-use1",
			keep_alive=True,
			user_data_dir=None,
			headless=False,
		)
	)
	await browser_session.start()

	current_agent = None
	llm = ChatOpenAI(model='gpt-4o', temperature=0.05)

	task1 = '''You are an automation bot for downloading Zepto vendor invoices. Follow these exact steps:

INITIAL LOGIN (Execute Once):
1. Navigate to Zepto vendor portal :https://brands.zepto.co.in/login
2. Enter email credentials: operations@sanfe.in
3. Enter password: Sanfezepto@9818
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
3. Check end date is auto set to 21 July 2025
4. Click Apply button
5. Wait for table to refresh
6. Click Download button (page 0)
7. Navigate to URL: https://brands.zepto.co.in/vendor/payments/invoices?invoiceStartDate=2025-07-01T00%3A00%3A00.000Z&invoiceEndDate=2025-07-19T23%3A59%3A59.999Z&pageNumber=1
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
✓ July 2025: Downloaded pages 0,1,2,3... until No Data found'''


	task2 = '''### NOW YOUR NEXT TASK IS TO EXECUTE THE FOLLOWING STEPS EXACTLY AS GIVEN BELOW:
Navigate to Zepto vendor portal :{ZEPTO_URL},check if it is already logged in or not, if not then login with email: {ZEPTO_EMAIL} and password: {ZEPTO_PASSWORD} and complete the OTP verification(user will do it manually).
GO TO THE DEBIT AND CREDIT nOTES SECTION IN THE PAYMENTS MENU PRESENT IN SIDE BAR MENU AND FOLLOW THE STEPS BELOW:
Just like invoices, you will download debit and credit notes for the same months as invoices. once page is opened you will see a date button with calendar icon on the left of Learning Hub button.click on it.
the date filter for debit and credit notes will be present somewhere in top left.set the start date to "1 May 2025" and check if  end date is set to "31 May 2025"  automatically and click apply button.
Now click on download button to download page 0.
now navigate to url"https://brands.zepto.co.in/vendor/payments/debit-credit-notes?tab=Debit+%26+Credit+Notes&startDate=2025-05-01T17%3A15%3A21.000Z&endDate=2025-05-31T17%3A15%3A21.000Z&pageNumber=1" this is next page .once loaded click on download button.
keep incrementing pageNumber in URL until you see "No Data found" message appears in center of page.
once you reach "No Data found" message, you will now change the date to next month i.e.  1 June 2025.
set the start date to "1 June 2025" and check if end date is set to "1 July 2025" automatically and click apply button.
Now click on download button to download page 0.
now navigate to url"https://brands.zepto.co.in/vendor/payments/debit-credit-notes?tab=Debit+%26+Credit+Notes&startDate=2025-06-01T17%3A15%3A21.000Z&endDate=2025-06-30T17%3A15%3A21.000Z&pageNumber=1" this is next page .once loaded click on download button.
keep incrementing pageNumber in URL until you see "No Data found" message appears in center of page.
once you reach "No Data found" message, you will now change the date to next month i.e.  1 July 2025.
set the start date to "1 July 2025" and check if end date is set to "21 July 2025" automatically and click apply button.
Now click on download button to download page 0.
now navigate to url"https://brands.zepto.co.in/vendor/payments/debit-credit-notes?tab=Debit+%26+Credit+Notes&startDate=2025-07-01T17%3A15%3A21.000Z&endDate=2025-07-19T17%3A15%3A21.000Z&pageNumber=1" this is next page .once loaded click on download button.
keep incrementing pageNumber in URL until you see "No Data found" message appears in center of page.
 once you reach "No Data found" message, you will now stop the task and close the browser.'''

	agent1 = Agent(
		task=task1,
		browser_session=browser_session,
		llm=llm,
	)
	agent2 = Agent(
		task=task2,
		browser_session=browser_session,
		llm=llm,
	)

	async def run_agent2_with_delay():
		await asyncio.sleep(30) 
		await agent2.run()

	await asyncio.gather(agent1.run(), run_agent2_with_delay())
	await browser_session.kill()


asyncio.run(main())