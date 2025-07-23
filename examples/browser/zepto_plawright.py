import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
ZEPTO_URL = os.getenv('zepto_url', 'https://brands.zepto.co.in/vendor/login')
ZEPTO_EMAIL = os.getenv('zepto_email')
ZEPTO_PASSWORD = os.getenv('zepto_password')
DOWNLOADS_PATH = r"C:\Users\RishitGupta\Desktop\browser-use1"

if not ZEPTO_EMAIL or not ZEPTO_PASSWORD:
    raise ValueError("ZEPTO_EMAIL or ZEPTO_PASSWORD is not set in .env file.")

async def wait_for_download_button(page):
    download_button = page.locator('button:has-text("Download")')
    await download_button.wait_for(state="visible", timeout=30000)
    while not await download_button.is_enabled():
        await asyncio.sleep(0.5)
    return download_button

async def wait_for_month_in_invoice_table(page, month_num, timeout=30):
    """Wait for the first visible invoice's date to match the target month number."""
    for _ in range(timeout * 2):
        try:
            # Assumes the "Invoice Booked Date" is in the 7th column. Adjust if needed.
            cell = await page.query_selector('tr:nth-of-type(2) td:nth-child(7)')
            if cell:
                cell_text = await cell.inner_text()
                if cell_text:
                    try:
                        parts = cell_text.split()
                        parsed = datetime.strptime(' '.join(parts[0:3]), "%d %b %Y")
                        if parsed.month == month_num:
                            return
                    except Exception:
                        pass
        except Exception:
            pass
        await asyncio.sleep(0.5)
    raise TimeoutError("Table did not update to show the correct month.")

async def reset_to_first_page(page):
    """Click the '1' pagination button if not already on the first page."""
    try:
        # This selector matches the "1" page button that is NOT currently active
        one_btn = page.locator('ul[aria-label="pagination"] li button:has-text("1")')
        if await one_btn.count():
            # Only click if not already active (has aria-current or is disabled)
            curr_page = await page.locator('ul[aria-label="pagination"] li[aria-current="true"]').count()
            if curr_page == 0 or not await one_btn.evaluate('el => el.parentElement.getAttribute("aria-current") === "true"'):
                if await one_btn.is_enabled():
                    await one_btn.click()
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(1)
                    print("Reset to first page.")
    except Exception as e:
        print(f"Could not reset to first page (might already be on first page): {e}")

async def download_all_pages(page, month_prefix, no_data_text):
    pagenum = 0
    while True:
        download_button = await wait_for_download_button(page)
        if pagenum == 0:
            async with page.expect_download() as download_info:
                await download_button.click()
            download = await download_info.value
            save_path = os.path.join(DOWNLOADS_PATH, f"{month_prefix}_page_{pagenum}.xlsx")
            await download.save_as(save_path)
            print(f"Downloaded {month_prefix} page {pagenum}: {save_path}")
        else:
            url = page.url
            if "pageNumber=" in url:
                base_url = url.split("&pageNumber=")[0]
            else:
                base_url = url
            next_page_url = f"{base_url}&pageNumber={pagenum}"
            await page.goto(next_page_url)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            download_button = await wait_for_download_button(page)
            if await page.is_visible(f"text={no_data_text}"):
                print(f"Reached end of {month_prefix} pages at page {pagenum}.")
                break
            async with page.expect_download() as download_info:
                await download_button.click()
            download = await download_info.value
            save_path = os.path.join(DOWNLOADS_PATH, f"{month_prefix}_page_{pagenum}.xlsx")
            await download.save_as(save_path)
            print(f"Downloaded {month_prefix} page {pagenum}: {save_path}")
        pagenum += 1

async def set_start_date(page, start_date_str, target_month_num):
    # Find and click the date range button
    range_buttons = await page.query_selector_all('button')
    range_button = None
    for btn in range_buttons:
        text = (await btn.inner_text()).strip()
        if " - " in text and "/" not in text and len(text) > 15:
            range_button = btn
            break
    if not range_button:
        raise Exception("Could not find the date range button.")
    await range_button.click()
    await asyncio.sleep(0.3)

    # Fill the start date input with the new date (format: dd/mm/yyyy)
    await page.wait_for_selector('input[placeholder="dd/mm/yyyy"]', timeout=10000)
    start_inputs = await page.query_selector_all('input[placeholder="dd/mm/yyyy"]')
    if not start_inputs:
        raise Exception("Could not find any start date input with placeholder 'dd/mm/yyyy'.")
    await start_inputs[0].fill(start_date_str)
    await asyncio.sleep(0.3)

    # Click "Apply"
    await page.wait_for_selector('button:has-text("Apply")', timeout=5000)
    await page.click('button:has-text("Apply")')
    await asyncio.sleep(2)

    # Wait for table to update to correct month
    await wait_for_month_in_invoice_table(page, target_month_num, timeout=30)
    print(f"Table updated to show month {target_month_num}")

    # Always reset to first page after date change
    await reset_to_first_page(page)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        await page.goto(ZEPTO_URL)
        await page.fill('input[type="email"]', str(ZEPTO_EMAIL))
        await page.fill('input[type="password"]', str(ZEPTO_PASSWORD))

        login_clicked = False
        for sel in [
            'button:has-text("Log In")',
            'button:has-text("LOG IN")',
            'button[type="submit"]',
            'input[type="submit"]',
            'button[class*="login"]',
            'button[data-testid*="login"]',
        ]:
            try:
                await page.click(sel, timeout=2000)
                print(f"Clicked login with selector: {sel}")
                login_clicked = True
                break
            except Exception:
                continue
        if not login_clicked:
            await page.press('input[type="password"]', 'Enter')
            print("Pressed Enter in password field as fallback")

        print("Please complete OTP verification in the browser, then click Confirm.")
        input("After OTP and Confirm, press Enter here to continue...")

        # Go to Invoices page
        await page.goto("https://brands.zepto.co.in/vendor/payments/invoices")
        await wait_for_download_button(page)

        # --- MAY 2025 ---
        print("Downloading May...")
        await set_start_date(page, "01/05/2025", target_month_num=5)
        await download_all_pages(page, "May", "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied.")

        # --- JUNE 2025 ---
        print("Downloading June...")
        await set_start_date(page, "01/06/2025", target_month_num=6)
        await download_all_pages(page, "Jun", "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied.")

        # --- JULY 2025 ---
        print("Downloading July...")
        await set_start_date(page, "02/07/2025", target_month_num=7)
        await download_all_pages(page, "Jul", "No Data found Sorry we couldn't find the data you were looking for. Try changing the filters that you have applied.")

        await browser.close()
        print("All downloads complete.")

if __name__ == "__main__":
    asyncio.run(main())