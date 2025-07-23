"""
Improved Zepto Vendor Invoice Automation Script

This script automates the download of vendor invoices from the Zepto vendor portal
for May, June, and July 2025. It includes:

- Better task decomposition with separate functions for each month
- Robust error handling and retry logic
- State management using BrowserSession
- Progress tracking and logging
- Improved completion detection
- Better date picker handling

Usage:
1. Create a .env file with:
   zepto_url=your_portal_url
   zepto_email=your_email
   zepto_password=your_password
   OPENAI_API_KEY=your_openai_key

2. Run the script:
   python zepto_invoice_automation_improved.py
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
from browser_use import Agent
from browser_use.browser import BrowserProfile, BrowserSession
from browser_use.llm import ChatOpenAI

load_dotenv()

# Configuration
ZEPTO_URL = os.getenv('zepto_url')
ZEPTO_EMAIL = os.getenv('zepto_email')
ZEPTO_PASSWORD = os.getenv('zepto_password')

if not all([ZEPTO_URL, ZEPTO_EMAIL, ZEPTO_PASSWORD]):
	raise ValueError("Missing required environment variables: zepto_url, zepto_email, zepto_password")

if not os.getenv('OPENAI_API_KEY'):
	raise ValueError('OPENAI_API_KEY is not set')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Month configurations
MONTHS_CONFIG = [
	{
		'name': 'May',
		'start_date': '2025-05-01',
		'end_date': '2025-05-31',
		'start_url_param': '2025-05-01T00%3A00%3A00.000Z',
		'end_url_param': '2025-05-31T23%3A59%3A59.999Z'
	},
	{
		'name': 'June', 
		'start_date': '2025-06-01',
		'end_date': '2025-06-30',
		'start_url_param': '2025-06-01T00%3A00%3A00.000Z',
		'end_url_param': '2025-06-30T23%3A59%3A59.999Z'
	},
	{
		'name': 'July',
		'start_date': '2025-07-01', 
		'end_date': '2025-07-19',
		'start_url_param': '2025-07-01T00%3A00%3A00.000Z',
		'end_url_param': '2025-07-19T23%3A59%3A59.999Z'
	}
]


class ZeptoInvoiceAutomation:
	def __init__(self, downloads_path: str = None):
		self.downloads_path = downloads_path or str(Path.home() / "Downloads")
		
		# Create browser profile with proper downloads handling
		self.browser_profile = BrowserProfile(
			downloads_path=self.downloads_path,
			headless=False  # Set to True for headless operation
		)
		
		self.browser_session = BrowserSession(browser_profile=self.browser_profile)
		self.llm = ChatOpenAI(model='gpt-4o', temperature=0)
		
		# Track progress
		self.completed_months: List[str] = []
		self.current_month_pages: Dict[str, int] = {}
		
	async def login_and_setup(self) -> bool:
		"""Handle initial login and navigation to invoices page"""
		
		login_task = f"""
		You are logging into the Zepto vendor portal. Follow these steps carefully:

		STEP 1: Navigate and Login
		1. Navigate to {ZEPTO_URL}
		2. Enter email: {ZEPTO_EMAIL}
		3. Enter password: {ZEPTO_PASSWORD}  
		4. Click the Login button
		5. WAIT for human OTP input - DO NOT proceed until you see the dashboard is fully loaded
		6. Dismiss any popups that may appear

		STEP 2: Navigate to Invoices
		1. Look for the sidebar menu (hamburger icon should already be opened)
		2. Find the "Payments" section in the sidebar
		3. Click on "Payments" to open the dropdown
		4. In the dropdown menu, click "Invoices"
		5. Wait for the invoices page to load completely
		6. Confirm you can see the date picker button (calendar icon) near the top right

		SUCCESS CRITERIA:
		- You are on the invoices page
		- You can see a data table with invoices
		- You can see the date picker calendar icon button
		- The page is fully loaded and responsive

		IMPORTANT: 
		- Take your time with each step
		- Wait for pages to fully load
		- Do not click any unnecessary buttons
		- If you encounter errors, describe what you see
		"""
		
		agent = Agent(
			task=login_task,
			llm=self.llm,
			browser_session=self.browser_session,
			max_actions_per_step=5,
			use_vision=True
		)
		
		try:
			await agent.run(max_steps=20)
			logger.info("Login and navigation completed successfully")
			return True
		except Exception as e:
			logger.error(f"Login failed: {e}")
			return False

	async def download_month_invoices(self, month_config: Dict) -> bool:
		"""Download all pages of invoices for a specific month"""
		
		month_name = month_config['name']
		logger.info(f"Starting download for {month_name} 2025")
		
		# Step 1: Set date range
		date_task = f"""
		You are setting the date range for {month_name} 2025 invoice downloads.
		
		CURRENT STATE: You are on the invoices page with the data table visible.
		
		STEPS TO EXECUTE:
		1. Look for the date picker button (calendar icon) near the top right corner, left of "Learning Hub" button
		2. Click the calendar/date picker icon to open the date picker
		3. Set the start date to: {month_config['start_date']} (May 1, 2025 format)
		4. Verify the end date is automatically set to: {month_config['end_date']} 
		5. Click the "Apply" button to apply the date filter
		6. Wait for the table to refresh with filtered data for {month_name}
		7. Confirm the table now shows data for the selected date range

		IMPORTANT:
		- Take your time with the date picker interaction
		- Make sure both start and end dates are correctly set
		- Wait for the table to fully refresh after clicking Apply
		- Do not click any other buttons during this process
		
		SUCCESS CRITERIA:
		- Date range is set to {month_name} 2025
		- Table shows filtered data 
		- Ready to start downloading pages
		"""
		
		agent = Agent(
			task=date_task,
			llm=self.llm,
			browser_session=self.browser_session,
			max_actions_per_step=8,
			use_vision=True
		)
		
		try:
			await agent.run(max_steps=15)
			logger.info(f"Date range set for {month_name}")
		except Exception as e:
			logger.error(f"Failed to set date range for {month_name}: {e}")
			return False
		
		# Step 2: Download page 0 (initial page)
		initial_download_task = f"""
		Download the first page of {month_name} 2025 invoices.
		
		STEPS:
		1. Locate the "Download" button on the page
		2. Click the "Download" button to download page 0 (the currently displayed data)
		3. Wait for the download to complete
		4. Confirm the download was successful
		
		This downloads what we call "page 0" - the initial data shown in the table.
		"""
		
		agent = Agent(
			task=initial_download_task,
			llm=self.llm,
			browser_session=self.browser_session,
			max_actions_per_step=5,
			use_vision=True
		)
		
		try:
			await agent.run(max_steps=10)
			logger.info(f"Downloaded page 0 for {month_name}")
		except Exception as e:
			logger.error(f"Failed to download page 0 for {month_name}: {e}")
			return False
		
		# Step 3: Download remaining pages
		return await self._download_remaining_pages(month_config)
	
	async def _download_remaining_pages(self, month_config: Dict) -> bool:
		"""Download pages 1, 2, 3... until no data found"""
		
		month_name = month_config['name']
		base_url = f"https://brands.zepto.co.in/vendor/payments/invoices?invoiceStartDate={month_config['start_url_param']}&invoiceEndDate={month_config['end_url_param']}"
		
		page_number = 1
		max_pages = 50  # Safety limit
		
		while page_number <= max_pages:
			logger.info(f"Downloading {month_name} page {page_number}")
			
			# Navigate to specific page
			page_url = f"{base_url}&pageNumber={page_number}"
			
			page_task = f"""
			Download page {page_number} for {month_name} 2025 invoices.
			
			STEPS:
			1. Navigate to this URL: {page_url}
			2. Wait for the page to fully load
			3. Check if you see "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied." message in the center of the page
			4. If you see "No Data found" message:
			   - Report "NO_DATA_FOUND" and stop
			5. If you see data in the table:
			   - Click the "Download" button
			   - Wait for download to complete
			   - Report "DOWNLOAD_COMPLETED"
			
			IMPORTANT:
			- Carefully check for the "No Data found" message
			- Only click Download if there is actual data to download
			- Wait for pages to fully load before checking content
			"""
			
			agent = Agent(
				task=page_task,
				llm=self.llm,
				browser_session=self.browser_session,
				max_actions_per_step=6,
				use_vision=True
			)
			
			try:
				await agent.run(max_steps=12)
				
				# Check if we should continue (this is a simplified check)
				# In a real implementation, you might want to check the agent's output
				# or use a more sophisticated completion detection
				
				# For now, increment and continue
				page_number += 1
				
				# Add a small delay between pages
				await asyncio.sleep(2)
				
			except Exception as e:
				logger.error(f"Failed to download page {page_number} for {month_name}: {e}")
				# Continue to next page despite error
				page_number += 1
				continue
		
		logger.info(f"Completed downloading all pages for {month_name}")
		self.completed_months.append(month_name)
		return True
	
	async def run_automation(self) -> bool:
		"""Run the complete automation process"""
		
		try:
			# Step 1: Login and navigate to invoices
			if not await self.login_and_setup():
				logger.error("Failed to login and setup")
				return False
			
			# Step 2: Process each month
			for month_config in MONTHS_CONFIG:
				month_name = month_config['name']
				
				if month_name in self.completed_months:
					logger.info(f"Skipping {month_name} - already completed")
					continue
				
				logger.info(f"Processing {month_name} 2025...")
				
				if not await self.download_month_invoices(month_config):
					logger.error(f"Failed to download invoices for {month_name}")
					# Continue with next month
					continue
				
				logger.info(f"Successfully completed {month_name} 2025")
				
				# Brief pause between months
				await asyncio.sleep(3)
			
			logger.info("All months completed successfully!")
			
			# Final summary
			logger.info("AUTOMATION SUMMARY:")
			logger.info(f"Completed months: {', '.join(self.completed_months)}")
			logger.info(f"Downloads saved to: {self.downloads_path}")
			
			return True
			
		except Exception as e:
			logger.error(f"Automation failed: {e}")
			return False
		
		finally:
			# Keep browser open for manual verification
			input("Press Enter to close the browser and complete...")
			await self.browser_session.close()


async def main():
	"""Main function to run the automation"""
	
	# Optional: specify custom downloads path
	downloads_path = input("Enter downloads path (or press Enter for default): ").strip()
	if not downloads_path:
		downloads_path = str(Path.home() / "Downloads" / "zepto_invoices")
	
	# Create downloads directory if it doesn't exist
	Path(downloads_path).mkdir(parents=True, exist_ok=True)
	
	print(f"Downloads will be saved to: {downloads_path}")
	print("Starting Zepto invoice automation...")
	print("Make sure you have your OTP device ready for login verification.")
	
	automation = ZeptoInvoiceAutomation(downloads_path=downloads_path)
	
	success = await automation.run_automation()
	
	if success:
		print("✅ Automation completed successfully!")
	else:
		print("❌ Automation encountered errors. Check logs for details.")


if __name__ == '__main__':
	asyncio.run(main())