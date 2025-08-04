import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load credentials from .env file
load_dotenv()
AMAZON_VENDOR_URL = "https://www.vendorcentral.in/"
AMAZON_VENDOR_RETURNS_URL = "https://www.vendorcentral.in/hz/vendor/members/returns-invoice-download?ref_=vc_xx_subNav"
AMAZON_EMAIL = os.getenv("amazon_email")
AMAZON_PASSWORD = os.getenv("amazon_password")

START_DATE = "07/01/2025"
END_DATE = "07/11/2025"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Go to login page
        await page.goto(AMAZON_VENDOR_URL)
        print("Navigated to Amazon Vendor Central login page.")

        # 2. Login
        await page.fill('input[name="email"]', AMAZON_EMAIL) # pyright: ignore[reportArgumentType]
        await page.click('input#continue')
        await asyncio.sleep(1)
        await page.fill('input[name="password"]', AMAZON_PASSWORD) # pyright: ignore[reportArgumentType]
        await page.click('input#signInSubmit')
        print("Submitted login form. Enter OTP if prompted.")

        # 3. Wait for user to enter OTP manually
        print("⏳ Please enter OTP manually in the browser window (if required)...")
        await page.wait_for_selector('text=Vendor Central', timeout=180000)
        print("✅ OTP entered and login successful!")

        # 4. Go to returns invoice download page
        await page.goto(AMAZON_VENDOR_RETURNS_URL)
        print("Navigated to returns invoice download page.")

        # 5. Wait for date fields to load (use placeholder as seen in screenshot)
        await page.wait_for_selector('input[placeholder="MM/DD/YYYY"]', timeout=20000)
        date_inputs = await page.query_selector_all('input[placeholder="MM/DD/YYYY"]')
        if len(date_inputs) < 2:
            raise Exception("Date input fields not found!")

        # 6. Type Start Date
        await date_inputs[0].click()
        await date_inputs[0].fill('')  # clear existing value
        await date_inputs[0].type(START_DATE)
        print(f"Start Date entered as {START_DATE}")

        # 7. Type End Date
        await date_inputs[1].click()
        await date_inputs[1].fill('')  # clear existing value
        await date_inputs[1].type(END_DATE)
        print(f"End Date entered as {END_DATE}")

        # 8. Click Submit button
        await page.click('button:has-text("Submit")')
        print("Clicked the submit button.")

        # Wait for results to load, or further automation
        await asyncio.sleep(10)

        print("Automation complete. Add file download automation if required.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())   #completed