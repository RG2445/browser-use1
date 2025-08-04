# type: ignore
import asyncio  # type: ignore
import os  # type: ignore
from dotenv import load_dotenv  # type: ignore
from playwright.async_api import async_playwright  # type: ignore

# Load credentials from .env file
load_dotenv()  # type: ignore
AMAZON_VENDOR_URL = "https://www.vendorcentral.in"  # type: ignore
RETURNS_URL = (
    "https://www.vendorcentral.in/katalmonsapp/vendor/members/returns?marketplace=IN&vendorCodes=1K7XI&searchText=&fromDate-d=30&fromDate-m=6&fromDate-y=2025&toDate-d=31&toDate-m=7&toDate-y=2025"
)  # type: ignore
AMAZON_EMAIL = os.getenv("amazon_email")  # type: ignore
AMAZON_PASSWORD = os.getenv("amazon_password")  # type: ignore

START_DATE = "01/07/2025"  # type: ignore
END_DATE = "11/07/2025"    # type: ignore

async def main():  # type: ignore
    async with async_playwright() as p:  # type: ignore
        browser = await p.chromium.launch(headless=False)  # type: ignore
        context = await browser.new_context()  # type: ignore
        page = await context.new_page()  # type: ignore

        # 1. Login
        await page.goto(AMAZON_VENDOR_URL)  # type: ignore
        await page.fill('input[name="email"]', AMAZON_EMAIL)  # type: ignore
        await page.click('input#continue')  # type: ignore
        await asyncio.sleep(1)  # type: ignore
        await page.fill('input[name="password"]', AMAZON_PASSWORD)  # type: ignore
        await page.click('input#signInSubmit')  # type: ignore
        print("Submitted login form. Enter OTP if prompted.")  # type: ignore

        # 2. Wait for OTP and successful login
        print("⏳ Please enter OTP manually in the browser window (if required)...")  # type: ignore
        await page.wait_for_selector('text=Vendor Central', timeout=180000)  # type: ignore
        print("✅ OTP entered and login successful!")  # type: ignore

        # 3. Go to Returns page
        await page.goto(RETURNS_URL)  # type: ignore
        print("Navigated to Returns page.")  # type: ignore

        # 4. Click the Date Range dropdown (not Vendor codes)
        await page.wait_for_selector('.select-header:has(.placeholder-text:has-text("/202"))', timeout=20000)  # type: ignore
        await page.click('.select-header:has(.placeholder-text:has-text("/202"))')  # type: ignore
        print('Clicked "Date Range" dropdown.')  # type: ignore

        # 5. Wait for dropdown options to be visible
        await page.wait_for_selector('.select-options:visible', timeout=5000)  # type: ignore
        print('Dropdown options are visible.')  # type: ignore

        # 6. Select "Custom Date Range"
        await asyncio.sleep(0.5)  # type: ignore
        options = await page.query_selector_all('.standard-option-name:visible')  # type: ignore
        found = False  # type: ignore
        for option in options:  # type: ignore
            text = (await option.inner_text()).strip().lower()  # type: ignore
            if text == "custom date range":  # type: ignore
                await option.click()  # type: ignore
                found = True  # type: ignore
                print('Selected "Custom Date Range".')  # type: ignore
                break  # type: ignore
        if not found:  # type: ignore
            raise Exception('"Custom Date Range" option not found!')  # type: ignore

        # 7. Input Start Date ("From:")
        await page.wait_for_selector('input[aria-label="From:"]', timeout=10000)  # type: ignore
        from_date_input = await page.query_selector('input[aria-label="From:"]')  # type: ignore
        await from_date_input.click()  # type: ignore
        await from_date_input.fill('')  # type: ignore
        await from_date_input.type(START_DATE)  # type: ignore
        print(f"From Date entered as {START_DATE}")  # type: ignore

        # 8. Input End Date ("To:")
        await page.wait_for_selector('input[aria-label="To:"]', timeout=10000)  # type: ignore
        to_date_input = await page.query_selector('input[aria-label="To:"]')  # type: ignore
        await to_date_input.click()  # type: ignore
        await to_date_input.fill('')  # type: ignore
        await to_date_input.type(END_DATE)  # type: ignore
        print(f"To Date entered as {END_DATE}")  # type: ignore

        # 9. Click Apply (using kat-button ID)
        await page.wait_for_selector('#data-range-modal-apply-button', timeout=10000)  # type: ignore
        await page.click('#data-range-modal-apply-button')  # type: ignore
        print('Clicked "Apply".')  # type: ignore

        # 10. Click on "Export all return summary"
        await page.wait_for_selector('span:has-text("Export all return summary")', timeout=10000)  # type: ignore
        await page.click('span:has-text("Export all return summary")')  # type: ignore
        print('Clicked "Export all return summary".')  # type: ignore

        await asyncio.sleep(10)  # type: ignore
        print("Automation complete.")  # type: ignore

        await browser.close()  # type: ignore

if __name__ == "__main__":  # type: ignore
    asyncio.run(main())  # completed