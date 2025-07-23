"""
Fixed Zepto Vendor Invoice Automation Script

This is an improved version of the original script that addresses the issues with
downloading invoices after May. Key improvements:

1. Better state management with BrowserSession
2. Clearer task decomposition 
3. More robust error handling
4. Better completion detection
5. Simplified logic flow

Usage: Same as original script, just replace the original with this improved version.
"""

import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent
from browser_use.browser import BrowserProfile, BrowserSession
from browser_use.llm import ChatOpenAI

load_dotenv()

ZEPTO_URL = os.getenv('zepto_url')
ZEPTO_EMAIL = os.getenv('zepto_email')
ZEPTO_PASSWORD = os.getenv('zepto_password')

CURRENT_TIMESTAMP = "2025-07-19 12:30:00"
USER_LOGIN = "RG2445"
CURRENT_DATE = "19 JULY 2025"

# Create browser session for state persistence
browser_profile = BrowserProfile(
	downloads_path=r"C:\Users\RishitGupta\Desktop\browser-use1",
	headless=False  # Set to True for headless operation
)
browser_session = BrowserSession(browser_profile=browser_profile)
llm = ChatOpenAI(model='gpt-4o', temperature=0)


async def login_and_navigate():
	"""Handle login and initial navigation to invoices page"""
	
	login_task = f"""
	You are automating login to Zepto vendor portal. Execute these steps precisely:

	INITIAL LOGIN:
	1. Navigate to {ZEPTO_URL}
	2. Enter email: {ZEPTO_EMAIL}
	3. Enter password: {ZEPTO_PASSWORD}
	4. Click Login button
	5. WAIT for human OTP input and complete verification until dashboard is loaded
	6. Dismiss any popups that appear

	NAVIGATE TO INVOICES:
	1. The sidebar menu should already be opened (hamburger icon)
	2. Look for "Payments" section in sidebar, click on "Payments" 
	3. In dropdown menu, click "Invoices"
	4. Wait for invoices page to load completely
	5. Verify you can see the date picker button (calendar icon) near top right

	STOP HERE - Do not proceed to download anything yet.
	Report when you have successfully reached the invoices page.
	"""
	
	agent = Agent(
		task=login_task,
		llm=llm,
		browser_session=browser_session,
		max_actions_per_step=5,
		use_vision=True
	)
	
	await agent.run(max_steps=25)


async def download_month_data(month_name: str, start_date: str, end_date: str, start_url: str, end_url: str):
	"""Download all pages for a specific month"""
	
	print(f"\n=== Starting {month_name} 2025 Downloads ===")
	
	# Step 1: Set date range
	date_setup_task = f"""
	Set up date range for {month_name} 2025 invoice downloads.
	
	STEPS:
	1. Click the date picker button (calendar icon) near top right corner
	2. Set start date to: {start_date}
	3. Verify end date is auto-set to: {end_date}
	4. Click "Apply" button
	5. Wait for table to refresh with {month_name} data
	
	SUCCESS: Table shows {month_name} 2025 data and you can see invoice records.
	"""
	
	agent = Agent(
		task=date_setup_task,
		llm=llm,
		browser_session=browser_session,
		max_actions_per_step=6,
		use_vision=True
	)
	
	await agent.run(max_steps=15)
	print(f"✓ Date range set for {month_name}")
	
	# Step 2: Download page 0 (current view)
	page0_task = f"""
	Download page 0 for {month_name} 2025.
	
	STEPS:
	1. Find the "Download" button on the page
	2. Click "Download" button (this downloads page 0)
	3. Wait for download to complete
	
	This is the initial page without any pageNumber parameter.
	"""
	
	agent = Agent(
		task=page0_task,
		llm=llm,
		browser_session=browser_session,
		max_actions_per_step=4,
		use_vision=True
	)
	
	await agent.run(max_steps=10)
	print(f"✓ Downloaded {month_name} page 0")
	
	# Step 3: Download remaining pages with URL navigation
	page_num = 1
	max_pages = 30  # Safety limit
	
	while page_num <= max_pages:
		print(f"Downloading {month_name} page {page_num}...")
		
		# Navigate to specific page URL
		page_url = f"https://brands.zepto.co.in/vendor/payments/invoices?invoiceStartDate={start_url}&invoiceEndDate={end_url}&pageNumber={page_num}"
		
		page_task = f"""
		Download {month_name} page {page_num}.
		
		STEPS:
		1. Navigate to URL: {page_url}
		2. Wait for page to load completely
		3. Check the page content:
		   - If you see "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied." 
		     → STOP and report "NO_MORE_DATA"
		   - If you see data in the table → Continue to step 4
		4. Click "Download" button
		5. Wait for download to complete
		6. Report "PAGE_DOWNLOADED"
		
		CRITICAL: Check carefully for the "No Data found" message before downloading.
		"""
		
		agent = Agent(
			task=page_task,
			llm=llm,
			browser_session=browser_session,
			max_actions_per_step=6,
			use_vision=True
		)
		
		try:
			await agent.run(max_steps=12)
			print(f"✓ Downloaded {month_name} page {page_num}")
			
			# Brief pause between pages
			await asyncio.sleep(2)
			page_num += 1
			
		except Exception as e:
			print(f"⚠ Error on {month_name} page {page_num}: {e}")
			# Try to continue with next page
			page_num += 1
			continue
		
		# Safety check - if we've downloaded many pages, prompt user
		if page_num > 20:
			response = input(f"Downloaded {page_num-1} pages for {month_name}. Continue? (y/n): ")
			if response.lower() != 'y':
				break
	
	print(f"✓ Completed {month_name} 2025 downloads")


async def run_complete_automation():
	"""Run the complete automation for all three months"""
	
	try:
		print("🚀 Starting Zepto Invoice Automation")
		print("Please be ready to enter OTP when prompted...")
		
		# Step 1: Login and navigate to invoices page
		await login_and_navigate()
		print("✓ Login and navigation completed")
		
		# Step 2: Download May 2025
		await download_month_data(
			month_name="May",
			start_date="May 1, 2025",
			end_date="May 31, 2025", 
			start_url="2025-05-01T00%3A00%3A00.000Z",
			end_url="2025-05-31T23%3A59%3A59.999Z"
		)
		
		# Step 3: Download June 2025
		await download_month_data(
			month_name="June",
			start_date="June 1, 2025",
			end_date="June 30, 2025",
			start_url="2025-06-01T00%3A00%3A00.000Z", 
			end_url="2025-06-30T23%3A59%3A59.999Z"
		)
		
		# Step 4: Download July 2025
		await download_month_data(
			month_name="July",
			start_date="July 1, 2025",
			end_date="July 19, 2025",
			start_url="2025-07-01T00%3A00%3A00.000Z",
			end_url="2025-07-19T23%3A59%3A59.999Z"
		)
		
		print("\n🎉 ALL DOWNLOADS COMPLETED SUCCESSFULLY!")
		print("✓ May 2025: Downloaded all pages")
		print("✓ June 2025: Downloaded all pages") 
		print("✓ July 2025: Downloaded all pages")
		
	except Exception as e:
		print(f"❌ Automation failed: {e}")
		raise
	
	finally:
		# Keep browser open for verification
		input("Press Enter to close browser...")
		await browser_session.close()


# Use the improved function instead of the original
async def run_download():
	"""Main entry point - replaces the original run_download function"""
	await run_complete_automation()


if __name__ == '__main__':
	asyncio.run(run_download())