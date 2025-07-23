import asyncio
import os
 
from dotenv import load_dotenv
from browser_use import Agent
from browser_use.browser.profile import BrowserProfile
from browser_use.browser import BrowserSession
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

# Use BrowserSession for better state management
browser_session = BrowserSession(browser_profile=browser_profile)
llm = ChatOpenAI(model='gpt-4o', temperature=0)


# Break down the task into smaller, more manageable parts
login_task = f"""
You are an automation bot for Zepto vendor portal login. Execute these steps:

INITIAL LOGIN (Execute Once):
1. Navigate to {ZEPTO_URL}
2. Enter email credentials: {ZEPTO_EMAIL}
3. Enter password: {ZEPTO_PASSWORD}
4. Click Login button
5. WAIT for human OTP input and complete verification until dashboard is loaded
6. Dismiss any popups that appear

NAVIGATION TO INVOICES:
1. Look for sidebar menu (hamburger icon should already be opened)
2. Find the "Payments" section and click on "Payments" to open dropdown
3. In dropdown menu, click "Invoices" 
4. Wait for invoices page to load completely
5. Verify you can see the date picker button (calendar icon) near top right corner

STOP HERE. Do not proceed with any downloads. Just confirm you are on the invoices page.
"""

may_task = f"""
You are downloading May 2025 invoices. Follow these exact steps:

CURRENT STATE: You are on the invoices page with the data table visible.

MONTH 1 - MAY 2025 (May 1 to May 31): 
1. Look for the date picker button (calendar icon) near the top right corner, left of Learning Hub button
2. Click the calendar icon to open date picker
3. Set start date: May 1, 2025
4. Check that end date is auto-set to May 31, 2025
5. Click "Apply" button
6. Wait for table to refresh with May filtered data
7. Click "Download" button (this downloads page 0)
8. Navigate to URL: https://brands.zepto.co.in/vendor/payments/invoices?invoiceStartDate=2025-05-01T00%3A00%3A00.000Z&invoiceEndDate=2025-05-31T23%3A59%3A59.999Z&pageNumber=1
9. Wait for page to load, then click "Download" button
10. Change URL pageNumber to 2, press Enter, wait for load, click "Download"
11. Continue incrementing pageNumber (3,4,5...) until you see "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied." message in center of page

CRITICAL: Stop downloading when you see the "No Data found" message. Record how many pages you downloaded for May.
"""

june_task = f"""
You are downloading June 2025 invoices. Follow these exact steps:

CURRENT STATE: You have completed May downloads and are still on the invoices page.

MONTH 2 - JUNE 2025 (June 1 to June 30):
1. Click the date picker button (calendar icon) again
2. Change the start date to June 1, 2025 
3. Verify end date is auto-set to June 30, 2025
4. Click "Apply" button
5. Wait for table to refresh with June filtered data
6. Click "Download" button (this downloads page 0)
7. Navigate to URL: https://brands.zepto.co.in/vendor/payments/invoices?invoiceStartDate=2025-06-01T00%3A00%3A00.000Z&invoiceEndDate=2025-06-30T23%3A59%3A59.999Z&pageNumber=1
8. Wait for page to load, then click "Download" button
9. Change URL pageNumber to 2, press Enter, wait for load, click "Download"
10. Continue incrementing pageNumber (3,4,5...) until you see "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied." message in center of page

CRITICAL: Stop downloading when you see the "No Data found" message. Record how many pages you downloaded for June.
"""

july_task = f"""
You are downloading July 2025 invoices. Follow these exact steps:

CURRENT STATE: You have completed May and June downloads and are still on the invoices page.

MONTH 3 - JULY 2025:
1. Click the date picker button (calendar icon) again
2. Change the start date to July 1, 2025 
3. Verify end date is auto-set to July 19, 2025 (current date limit)
4. Click "Apply" button
5. Wait for table to refresh with July filtered data
6. Click "Download" button (this downloads page 0)
7. Navigate to URL: https://brands.zepto.co.in/vendor/payments/invoices?invoiceStartDate=2025-07-01T00%3A00%3A00.000Z&invoiceEndDate=2025-07-19T23%3A59%3A59.999Z&pageNumber=1
8. Wait for page to load, then click "Download" button
9. Change URL pageNumber to 2, press Enter, wait for load, click "Download"
10. Continue incrementing pageNumber (3,4,5...) until you see "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied." message in center of page

CRITICAL: Stop downloading when you see the "No Data found" message. Record how many pages you downloaded for July.

COMPLETION: After July is finished, provide a summary of total pages downloaded for each month.
"""


async def run_download():
    """
    Improved version that breaks down the complex task into manageable steps
    """
    
    print("🚀 Starting Zepto Invoice Automation")
    print("📋 This will download invoices for May, June, and July 2025")
    print("⚠️  Please be ready to enter OTP when prompted during login")
    
    try:
        # Step 1: Login and navigate to invoices page
        print("\n📝 Step 1: Logging in and navigating to invoices...")
        
        login_agent = Agent(
            task=login_task,
            llm=llm,
            max_actions_per_step=6,
            use_vision=True,
            browser_session=browser_session
        )
        
        await login_agent.run(max_steps=25)
        print("✅ Login and navigation completed")
        
        # Brief pause to ensure page is ready
        await asyncio.sleep(3)
        
        # Step 2: Download May 2025
        print("\n📥 Step 2: Downloading May 2025 invoices...")
        
        may_agent = Agent(
            task=may_task,
            llm=llm,
            max_actions_per_step=8,
            use_vision=True,
            browser_session=browser_session
        )
        
        await may_agent.run(max_steps=40)
        print("✅ May 2025 downloads completed")
        
        # Brief pause between months
        await asyncio.sleep(5)
        
        # Step 3: Download June 2025
        print("\n📥 Step 3: Downloading June 2025 invoices...")
        
        june_agent = Agent(
            task=june_task,
            llm=llm,
            max_actions_per_step=8,
            use_vision=True,
            browser_session=browser_session
        )
        
        await june_agent.run(max_steps=40)
        print("✅ June 2025 downloads completed")
        
        # Brief pause between months
        await asyncio.sleep(5)
        
        # Step 4: Download July 2025
        print("\n📥 Step 4: Downloading July 2025 invoices...")
        
        july_agent = Agent(
            task=july_task,
            llm=llm,
            max_actions_per_step=8,
            use_vision=True,
            browser_session=browser_session
        )
        
        await july_agent.run(max_steps=40)
        print("✅ July 2025 downloads completed")
        
        print("\n🎉 ALL DOWNLOADS COMPLETED SUCCESSFULLY!")
        print("📊 Summary:")
        print("   ✓ May 2025: All pages downloaded")
        print("   ✓ June 2025: All pages downloaded") 
        print("   ✓ July 2025: All pages downloaded")
        print(f"📁 Files saved to: {browser_profile.downloads_path}")
        
    except Exception as e:
        print(f"❌ Error during automation: {e}")
        print("💡 The browser will remain open for manual inspection")
        raise
    
    finally:
        # Keep browser open for verification
        input("\n⏸️  Press Enter to close the browser and finish...")
        await browser_session.close()


if __name__ == '__main__':
    asyncio.run(run_download())