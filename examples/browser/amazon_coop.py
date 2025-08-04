import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load credentials from .env file
load_dotenv()
AMAZON_VENDOR_URL = "https://www.vendorcentral.in"
COOP_URL = "https://www.vendorcentral.in/hz/vendor/members/coop?ref_=vc_xx_subNav"
AMAZON_EMAIL = os.getenv("amazon_email")
AMAZON_PASSWORD = os.getenv("amazon_password")

START_DATE = "1/7/2025"
END_DATE = "11/7/2025"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Login
        await page.goto(AMAZON_VENDOR_URL)
        await page.fill('input[name="email"]', AMAZON_EMAIL) # pyright: ignore[reportArgumentType]
        await page.click('input#continue')
        await asyncio.sleep(1)
        await page.fill('input[name="password"]', AMAZON_PASSWORD) # pyright: ignore[reportArgumentType]
        await page.click('input#signInSubmit')
        print("Submitted login form. Enter OTP if prompted.")

        # 2. Wait for OTP
        print("⏳ Please enter OTP manually in the browser window (if required)...")
        await page.wait_for_selector('text=Vendor Central', timeout=180000)
        print("✅ OTP entered and login successful!")

        # 3. Go to COOP page
        await page.goto(COOP_URL)
        print("Navigated to COOP page.")

        # 4. Wait for date inputs to appear
        await page.wait_for_selector('input[placeholder]', timeout=20000)
        date_inputs = await page.query_selector_all('input[placeholder]')
        if len(date_inputs) < 2:
            raise Exception("Date input fields not found!")

        # 5. Type Start Date (calendar opens)
        await date_inputs[0].click()
        await date_inputs[0].fill('')
        await date_inputs[0].type(START_DATE)
        print(f"Start Date entered as {START_DATE}")

        # 6. Immediately click End Date input (calendar switches to end date)
        await date_inputs[1].click()
        await date_inputs[1].fill('')
        await date_inputs[1].type(END_DATE)
        print(f"End Date entered as {END_DATE}")

        # 7. Click outside to close the end date calendar (click neutral area)
        # Try clicking the page body, or a header, or another non-input element
        try:
            await page.click('h1')  # If there's a visible heading
        except:
            try:
                await page.click('body', position={"x":1,"y":1})
            except:
                # fallback: click at a neutral position on the page
                await page.mouse.click(10, 10)
        print("Closed end date calendar.")

        # 8. Click 'Search' button
        await page.click('button:has-text("Search")')
        print("Clicked Search.")

        # 9. Select all
        # 8. Click 'Select all' link (correct selector)
        await page.wait_for_selector('#select-all', timeout=20000)
        await page.click('#select-all')
        print("Selected all results.")

        # 10. Export to spreadsheet from dropdown
        await page.wait_for_selector('select', timeout=20000)
        dropdown = await page.query_selector('select')
        await dropdown.select_option(label="Export to a spreadsheet") # pyright: ignore[reportOptionalMemberAccess]
        print("Chose 'Export to a spreadsheet' in dropdown.")

        await asyncio.sleep(10)
        print("Automation complete.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main()) #completed