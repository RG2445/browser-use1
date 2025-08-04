# type: ignore
import asyncio  # type: ignore
import os  # type: ignore
from dotenv import load_dotenv  # type: ignore
from playwright.async_api import async_playwright  # type: ignore

# Load credentials from .env file
load_dotenv()  # type: ignore
AMAZON_VENDOR_URL = "https://www.vendorcentral.in"  # type: ignore
INVENTORY_MGMT_URL = "https://www.vendorcentral.in/hz/vendor/members/inv-mgmt/home?ref_=vc_xx_subNav"  # type: ignore
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

        # 3. Go to Inventory Management page
        await page.goto(INVENTORY_MGMT_URL)  # type: ignore
        print("Navigated to Inventory Management page.")  # type: ignore

        # 4. Click on 'Download reports'
        await page.wait_for_selector('a:has-text("Download reports")', timeout=20000)  # type: ignore
        await page.click('a:has-text("Download reports")')  # type: ignore
        print("Clicked 'Download reports'.")  # type: ignore

        # 5. Open "Select the Vendor Codes" dropdown
        await page.wait_for_selector('.select-header:has(.placeholder-text:has-text("Select the Vendor Codes"))', timeout=20000)  # type: ignore
        await page.click('.select-header:has(.placeholder-text:has-text("Select the Vendor Codes"))')  # type: ignore
        print('Clicked "Select the Vendor Codes" dropdown.')  # type: ignore
        await asyncio.sleep(1.2)  # type: ignore

        # 6. Click "All" checkbox inside dropdown
        try:
            await page.wait_for_selector('kat-checkbox[label="All"]', timeout=5000)  # type: ignore
            await page.click('kat-checkbox[label="All"]')  # type: ignore
            print('Clicked "All" checkbox.')  # type: ignore
        except Exception:  # type: ignore
            dropdown = page.locator('kat-dropdown[label="Vendor Codes"]')  # type: ignore
            all_checkbox = (
                dropdown
                .locator('shadow=kat-checkbox[label="All"]')
                .locator('shadow=div[part="checkbox-check"]')
            )  # type: ignore
            await all_checkbox.wait_for(state='visible', timeout=5000)  # type: ignore
            await all_checkbox.click()  # type: ignore
            print('Clicked "All" checkbox inside shadow DOM.')  # type: ignore

        await asyncio.sleep(1)  # type: ignore

        # 7. Click on "Custom Date Range"
        await page.wait_for_selector('kat-radiobutton[label="Custom Date Range"]', timeout=10000)  # type: ignore
        await page.locator('kat-radiobutton[label="Custom Date Range"]').click(force=True)  # type: ignore
        print('Selected "Custom Date Range".')  # type: ignore

        # 8. Input Start Date ("Start Date")
        await page.wait_for_selector('input[aria-label="Start Date"]', timeout=10000)  # type: ignore
        start_date_input = await page.query_selector('input[aria-label="Start Date"]')  # type: ignore
        await start_date_input.click()  # type: ignore
        await start_date_input.fill('')  # type: ignore
        await start_date_input.type(START_DATE)  # type: ignore
        print(f"Start Date entered as {START_DATE}")  # type: ignore
        box = await page.evaluate("""() => {
            const w = window.innerWidth || document.documentElement.clientWidth;
            const h = window.innerHeight || document.documentElement.clientHeight;
            return {x: Math.floor(w/2), y: Math.floor(h/2)};
        }""")
        await page.mouse.click(box['x'], box['y'])  # type: ignore
        await asyncio.sleep(0.4)  # type: ignore

        # 9. Input End Date ("End Date")
        await page.wait_for_selector('input[aria-label="End Date"]', timeout=10000)  # type: ignore
        end_date_input = await page.query_selector('input[aria-label="End Date"]')  # type: ignore
        await end_date_input.click()  # type: ignore
        await end_date_input.fill('')  # type: ignore
        await end_date_input.type(END_DATE)  # type: ignore
        print(f"End Date entered as {END_DATE}")  # type: ignore

        # 10. Click in the center of the page to close any calendar overlays (only once)
        box = await page.evaluate("""() => {
            const w = window.innerWidth || document.documentElement.clientWidth;
            const h = window.innerHeight || document.documentElement.clientHeight;
            return {x: Math.floor(w/2), y: Math.floor(h/2)};
        }""")
        await page.mouse.click(box['x'], box['y'])  # type: ignore
        await asyncio.sleep(0.4)  # type: ignore

        # 11. Click "Generate Report"
        await page.wait_for_selector('button:has-text("Generate Report")', timeout=10000)  # type: ignore
        await page.click('button:has-text("Generate Report")', force=True)  # type: ignore
        print('Clicked "Generate Report".')  # type: ignore

        await asyncio.sleep(10)  # type: ignore
        print("Automation complete.")  # type: ignore

        await browser.close()  # type: ignore

if __name__ == "__main__":  # type: ignore
    asyncio.run(main())  # type: ignore