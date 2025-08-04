# type: ignore
import asyncio  # type: ignore
import os  # type: ignore
from dotenv import load_dotenv
from playwright.async_api import async_playwright  # type: ignore
from pathlib import Path

load_dotenv()  # type: ignore

AMAZON_VENDOR_URL = "https://www.vendorcentral.in"
COOP_URL = "https://www.vendorcentral.in/hz/vendor/members/coop?ref_=vc_xx_subNav"
INVENTORY_MGMT_URL = "https://www.vendorcentral.in/hz/vendor/members/inv-mgmt/home?ref_=vc_xx_subNav"
RETURNS_URL = (
    "https://www.vendorcentral.in/katalmonsapp/vendor/members/returns?marketplace=IN&vendorCodes=1K7XI&searchText=&fromDate-d=30&fromDate-m=6&fromDate-y=2025&toDate-d=31&toDate-m=7&toDate-y=2025"
)
AMAZON_VENDOR_RETURNS_URL = "https://www.vendorcentral.in/hz/vendor/members/returns-invoice-download?ref_=vc_xx_subNav"
RECON_URL = "https://www.vendorcentral.in/spv/vendorrecon"

AMAZON_EMAIL = os.getenv("amazon_email")
AMAZON_PASSWORD = os.getenv("amazon_password")

START_DATE = "01/07/2025"  # DD/MM/YYYY
END_DATE = "11/07/2025"    # DD/MM/YYYY
COOP_START_DATE = "1/7/2025"    # D/M/YYYY
COOP_END_DATE = "11/7/2025"     # D/M/YYYY
RETURNS_INVOICE_START_DATE = "07/01/2025"  # MM/DD/YYYY
RETURNS_INVOICE_END_DATE = "07/11/2025"    # MM/DD/YYYY

DESKTOP_PATH = str(Path.home() / "Desktop")  # Download to user's Desktop

async def download_and_rename(page, trigger_selector, function_name, start_date, end_date):
    # Listen for download event, click, then move and rename
    async with page.expect_download() as download_info:
        await page.click(trigger_selector)
    download = await download_info.value
    ext = Path(download.suggested_filename).suffix
    filename = f"{function_name}_{start_date}_{end_date}{ext}"
    dest_path = os.path.join(DESKTOP_PATH, filename)
    await download.save_as(dest_path)
    print(f"Downloaded and renamed to {filename} on Desktop.")

async def login_once(page):
    await page.goto(AMAZON_VENDOR_URL)
    await page.fill('input[name="email"]', AMAZON_EMAIL)
    await page.click('input#continue')
    await asyncio.sleep(1)
    await page.fill('input[name="password"]', AMAZON_PASSWORD)
    await page.click('input#signInSubmit')
    print("Submitted login form. Enter OTP if prompted.")
    print("⏳ Please enter OTP manually in the browser window (if required)...")
    await page.wait_for_selector('text=Vendor Central', timeout=180000)
    print("✅ OTP entered and login successful!")

async def coop_task(page):
    await page.goto(COOP_URL)
    print("Navigated to COOP page.")
    await page.wait_for_selector('input[placeholder]', timeout=20000)
    date_inputs = await page.query_selector_all('input[placeholder]')
    if len(date_inputs) < 2:
        raise Exception("Date input fields not found!")
    await date_inputs[0].click()
    await date_inputs[0].fill('')
    await date_inputs[0].type(COOP_START_DATE)
    print(f"COOP Start Date entered as {COOP_START_DATE}")
    await date_inputs[1].click()
    await date_inputs[1].fill('')
    await date_inputs[1].type(COOP_END_DATE)
    print(f"COOP End Date entered as {COOP_END_DATE}")
    # Click in the center to close calendar
    box = await page.evaluate("""() => {
        const w = window.innerWidth || document.documentElement.clientWidth;
        const h = window.innerHeight || document.documentElement.clientHeight;
        return {x: Math.floor(w/2), y: Math.floor(h/2)};
    }""")
    await page.mouse.click(box['x'], box['y'])
    print("Closed end date calendar.")
    await page.click('button:has-text("Search")')
    print("Clicked Search.")
    await page.wait_for_selector('#select-all', timeout=20000)
    await page.click('#select-all')
    print("Selected all results.")
    await page.wait_for_selector('select', timeout=20000)
    dropdown = await page.query_selector('select')
    await dropdown.select_option(label="Export to a spreadsheet")
    print("Chose 'Export to a spreadsheet' in dropdown.")
    print("COOP Automation complete.")

async def inventory_mgmt_task(page):
    await page.goto(INVENTORY_MGMT_URL)
    print("Navigated to Inventory Management page.")
    await page.wait_for_selector('a:has-text("Download reports")', timeout=20000)
    await page.click('a:has-text("Download reports")')
    print("Clicked 'Download reports'.")
    await page.wait_for_selector('.select-header:has(.placeholder-text:has-text("Select the Vendor Codes"))', timeout=20000)
    await page.click('.select-header:has(.placeholder-text:has-text("Select the Vendor Codes"))')
    print('Clicked "Select the Vendor Codes" dropdown.')
    await asyncio.sleep(1.2)
    try:
        await page.wait_for_selector('kat-checkbox[label="All"]', timeout=5000)
        await page.click('kat-checkbox[label="All"]')
        print('Clicked "All" checkbox.')
    except Exception:
        await page.evaluate("""
        () => {
            const dropdown = document.querySelector('kat-dropdown[label="Vendor Codes"]');
            if (!dropdown) return;
            const shadow = dropdown.shadowRoot;
            if (!shadow) return;
            const katCheckbox = shadow.querySelector('kat-checkbox[label="All"]');
            if (!katCheckbox) return;
            const katCheckboxShadow = katCheckbox.shadowRoot;
            if (!katCheckboxShadow) return;
            const checkboxDiv = katCheckboxShadow.querySelector('div[part="checkbox-check"]');
            if (checkboxDiv) checkboxDiv.click();
        }
        """)
        print('Clicked "All" checkbox inside shadow DOM.')
    await asyncio.sleep(1)
    await page.wait_for_selector('kat-radiobutton[label="Custom Date Range"]', timeout=10000)
    await page.locator('kat-radiobutton[label="Custom Date Range"]').click(force=True)
    print('Selected "Custom Date Range".')
    await page.wait_for_selector('input[aria-label="Start Date"]', timeout=10000)
    start_date_input = await page.query_selector('input[aria-label="Start Date"]')
    await start_date_input.click()
    await start_date_input.fill('')
    await start_date_input.type(START_DATE)
    print(f"Start Date entered as {START_DATE}")
    box = await page.evaluate("""() => {
        const w = window.innerWidth || document.documentElement.clientWidth;
        const h = window.innerHeight || document.documentElement.clientHeight;
        return {x: Math.floor(w/2), y: Math.floor(h/2)};
    }""")
    await page.mouse.click(box['x'], box['y'])
    await asyncio.sleep(0.4)
    await page.wait_for_selector('input[aria-label="End Date"]', timeout=10000)
    end_date_input = await page.query_selector('input[aria-label="End Date"]')
    await end_date_input.click()
    await end_date_input.fill('')
    await end_date_input.type(END_DATE)
    print(f"End Date entered as {END_DATE}")
    await page.mouse.click(box['x'], box['y'])
    await asyncio.sleep(0.4)
    await page.wait_for_selector('button:has-text("Generate Report")', timeout=10000)
    await page.click('button:has-text("Generate Report")', force=True)
    print('Clicked "Generate Report".')

async def returns_export_task(page):
    await page.goto(RETURNS_URL)
    print("Navigated to Returns page.")
    await page.wait_for_selector('.select-header:has(.placeholder-text:has-text("/202"))', timeout=20000)
    await page.click('.select-header:has(.placeholder-text:has-text("/202"))')
    print('Clicked "Date Range" dropdown.')
    await page.wait_for_selector('.select-options:visible', timeout=5000)
    print('Dropdown options are visible.')
    await asyncio.sleep(0.5)
    options = await page.query_selector_all('.standard-option-name:visible')
    found = False
    for option in options:
        text = (await option.inner_text()).strip().lower()
        if text == "custom date range":
            await option.click()
            found = True
            print('Selected "Custom Date Range".')
            break
    if not found:
        raise Exception('"Custom Date Range" option not found!')
    await page.wait_for_selector('input[aria-label="From:"]', timeout=10000)
    from_date_input = await page.query_selector('input[aria-label="From:"]')
    await from_date_input.click()
    await from_date_input.fill('')
    await from_date_input.type(START_DATE)
    print(f"From Date entered as {START_DATE}")
    await page.wait_for_selector('input[aria-label="To:"]', timeout=10000)
    to_date_input = await page.query_selector('input[aria-label="To:"]')
    await to_date_input.click()
    await to_date_input.fill('')
    await to_date_input.type(END_DATE)
    print(f"To Date entered as {END_DATE}")
    await page.wait_for_selector('#data-range-modal-apply-button', timeout=10000)
    await page.click('#data-range-modal-apply-button')
    print('Clicked "Apply".')
    await page.wait_for_selector('span:has-text("Export all return summary")', timeout=60000)
    await download_and_rename(page, 'span:has-text("Export all return summary")', "returns_export_task", START_DATE, END_DATE)
    print("Returns Export Automation complete.")

async def returns_invoice_task(page):
    await page.goto(AMAZON_VENDOR_RETURNS_URL)
    print("Navigated to returns invoice download page.")
    await page.wait_for_selector('input[placeholder="MM/DD/YYYY"]', timeout=20000)
    date_inputs = await page.query_selector_all('input[placeholder="MM/DD/YYYY"]')
    if len(date_inputs) < 2:
        raise Exception("Date input fields not found!")
    await date_inputs[0].click()
    await date_inputs[0].fill('')
    await date_inputs[0].type(RETURNS_INVOICE_START_DATE)
    print(f"Start Date entered as {RETURNS_INVOICE_START_DATE}")
    await date_inputs[1].click()
    await date_inputs[1].fill('')
    await date_inputs[1].type(RETURNS_INVOICE_END_DATE)
    print(f"End Date entered as {RETURNS_INVOICE_END_DATE}")
    box = await page.evaluate("""() => {
        const w = window.innerWidth || document.documentElement.clientWidth;
        const h = window.innerHeight || document.documentElement.clientHeight;
        return {x: Math.floor(w/2), y: Math.floor(h/2)};
    }""")
    await page.mouse.click(box['x'], box['y'])
    await page.wait_for_selector('button:has-text("Submit")', timeout=10000)
    await page.click('button:has-text("Submit")')
    print("Clicked 'Submit'.")
    print("Returns Invoice Automation complete.")

async def recon_download_first(page):
    await page.goto(RECON_URL)
    print("Navigated to vendor reconciliation page.")
    # Wait for any download button (assuming text "Download" or button[Download])
    # Try button or link with Download text, or fallback to first <a> with download href
    try:
        await page.wait_for_selector('a:has-text("Download"),button:has-text("Download")', timeout=15000)
        # Find all download links/buttons and click the first
        download_elements = await page.query_selector_all('a:has-text("Download"),button:has-text("Download")')
        if not download_elements:
            raise Exception("No download buttons found!")
        # Listen for download and click the first one
        async with page.expect_download() as download_info:
            await download_elements[0].click()
        download = await download_info.value
        ext = Path(download.suggested_filename).suffix
        filename = f"recon_download_first{ext}"
        dest_path = os.path.join(DESKTOP_PATH, filename)
        await download.save_as(dest_path)
        print(f"Reconciliation: Downloaded and saved as {filename} on Desktop.")
    except Exception as e:
        print(f"Recon Download: {e}")

async def click_file1_download(page):
    await page.goto(AMAZON_VENDOR_RETURNS_URL)
    print("Navigated (again) to returns invoice download page for File 1.")
    # The File 1 link is a span inside <a> with .link and text "File 1"
    await page.wait_for_selector('a.link span.link__inner:text("File 1")', timeout=15000)
    file1_span = await page.query_selector('a.link span.link__inner:text("File 1")')
    if file1_span is None:
        raise Exception("File 1 download link not found!")
    # Listen for download and click span (or parent <a>)
    parent_a = await file1_span.evaluate_handle('el => el.closest("a")')
    async with page.expect_download() as download_info:
        await parent_a.click()
    download = await download_info.value
    ext = Path(download.suggested_filename).suffix
    filename = f"returns_invoice_file1{ext}"
    dest_path = os.path.join(DESKTOP_PATH, filename)
    await download.save_as(dest_path)
    print(f"Downloaded File 1 as {filename} on Desktop.")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        # Login once
        await login_once(page)

        # Task 1: COOP
        await coop_task(page)
        # Task 2: Inventory Management
        await inventory_mgmt_task(page)
        # Task 3: Returns Export
        await returns_export_task(page)
        # Task 4: Returns Invoice Download
        await returns_invoice_task(page)

        # Go to recon page, download first file
        await recon_download_first(page)

        # Go to returns invoice download and click File 1 link
        await click_file1_download(page)

        print("All automations complete.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())