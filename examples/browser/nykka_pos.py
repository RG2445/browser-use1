import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import zipfile
import shutil
load_dotenv()

NYKAA_URL = os.getenv("nykaa_url", "https://seller.nykaa.com/login")
NYKAA_EMAIL = os.getenv("nykaa_email")
if NYKAA_EMAIL is None:
    raise ValueError("nykaa_email environment variable is not set.")

DOWNLOAD_DIR = Path(os.path.expanduser("~/Desktop/nykaa_downloads"))
PDF_DIR = Path(os.path.expanduser("~/Desktop/nykaa_pdfs"))

def extract_pdfs(zip_path: Path, pdf_dir: Path):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.namelist():
            if member.lower().endswith('.pdf'):
                zf.extract(member, pdf_dir)
                extracted = pdf_dir / member
                if extracted.parent != pdf_dir:
                    extracted.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(extracted), str(pdf_dir / extracted.name))
                    try:
                        extracted.parent.rmdir()
                    except Exception:
                        pass

async def select_pending_invoice_tab(page, max_attempts=6):
    """Force-select the 'Pending Invoice' tab by click and color check, and ensure Upcoming is NOT selected."""
    for attempt in range(max_attempts):
        await page.wait_for_selector('div.tab-option[aria-label="Pending Invoice"]', timeout=10000)
        await page.wait_for_selector('div.tab-option[aria-label="Upcoming"]', timeout=10000)
        pending_tab = await page.query_selector('div.tab-option[aria-label="Pending Invoice"]')
        upcoming_tab = await page.query_selector('div.tab-option[aria-label="Upcoming"]')
        if not pending_tab or not upcoming_tab:
            raise Exception('Pending Invoice or Upcoming tab not found!')
        await pending_tab.click(force=True)
        await asyncio.sleep(1.2)
        # Check computed color for both tabs
        pending_color = await pending_tab.evaluate("el => getComputedStyle(el).color")
        upcoming_color = await upcoming_tab.evaluate("el => getComputedStyle(el).color")
        print(f"[Try {attempt+1}] Pending Invoice color: {pending_color}, Upcoming color: {upcoming_color}")
        if pending_color.strip() == "rgb(232, 0, 113)" and (
            upcoming_color.strip() == "rgba(0, 19, 37, 0.64)" or
            upcoming_color.strip() == "rgb(0, 19, 37)"
        ):
            print("✅ Pending Invoice tab is selected by color and Upcoming is not selected.")
            return
    raise Exception("Failed to select Pending Invoice tab by color after several attempts.")

async def scroll_and_gather_new_downloads(page, scroll_container_selector, already_downloaded_pos):
    """Scrolls the container, gathers new download buttons not already downloaded (by PO), returns them."""
    all_new_downloads = []
    last_row_count = -1
    for _ in range(60):
        # Get visible table
        tables = await page.query_selector_all('table')
        visible_table = None
        for t in tables:
            is_hidden = await t.evaluate('el => el.offsetParent === null')
            if not is_hidden:
                visible_table = t
                break
        if not visible_table:
            break

        trs = await visible_table.query_selector_all('tbody tr')
        for row in trs:
            first_td = await row.query_selector('td:nth-child(2)')
            po_number = await first_td.inner_text() if first_td else None
            if not po_number or po_number.strip() in already_downloaded_pos:
                continue
            download_icon = await row.query_selector('td .download-coloum')
            if download_icon:
                all_new_downloads.append((po_number.strip(), download_icon))
                already_downloaded_pos.add(po_number.strip())
        # Scroll
        row_count = len(trs)
        if row_count == last_row_count:
            break
        last_row_count = row_count
        await page.evaluate(f'''
            () => {{
                const container = document.querySelector('{scroll_container_selector}');
                if (container) container.scrollTop = container.scrollHeight;
            }}
        ''')
        await asyncio.sleep(1.1)
    return all_new_downloads

async def main():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        await page.goto(NYKAA_URL)
        await page.fill('#cm-name, input[type="email"]', NYKAA_EMAIL) # pyright: ignore[reportArgumentType]
        await page.click('button[aria-label="Login to Nykaa"]')
        print("⏳ Please enter OTP manually in the browser...")


        await page.wait_for_selector('text=Warehouse Appointments Listing', timeout=60000)
        print("✅ Dashboard loaded, going to PO Listing page...")

        await page.goto("https://seller.nykaa.com/warehouse/po-listing")
        await page.wait_for_selector("text=Purchase Orders Listing", timeout=20000)
        print("✅ PO Listing page loaded.")

        print("🔄 Forcing click on Pending Invoice tab by color...")
        await select_pending_invoice_tab(page)

        scroll_container_selector = ".master-table-component-wrapper"
        await page.wait_for_selector(f"{scroll_container_selector} table", timeout=20000)
        print("🔽 Downloading visible rows first...")

        # Download visible first
        tables = await page.query_selector_all('table')
        visible_table = None
        for t in tables:
            is_hidden = await t.evaluate('el => el.offsetParent === null')
            if not is_hidden:
                visible_table = t
                break
        if not visible_table:
            print("No visible table found under Pending Invoice!")
            return

        already_downloaded_pos = set()
        trs = await visible_table.query_selector_all('tbody tr')
        for idx, row in enumerate(trs, 1):
            first_td = await row.query_selector('td:nth-child(2)')
            po_number = await first_td.inner_text() if first_td else None
            if not po_number:
                continue
            po_number = po_number.strip()
            download_icon = await row.query_selector('td .download-coloum')
            if not download_icon:
                continue
            print(f"➡️ Downloading for PO: {po_number} (row {idx}) ...")
            try:
                async with page.expect_download() as download_info:
                    await download_icon.click(force=True)
                download = await download_info.value
                target_file = DOWNLOAD_DIR / f"{po_number}.zip"
                await download.save_as(str(target_file))
                print(f"✅ Saved file to {target_file}")
                extract_pdfs(target_file, PDF_DIR)
                print(f"📄 Extracted PDFs from {target_file} to {PDF_DIR}")
                already_downloaded_pos.add(po_number)
            except Exception as e:
                print(f"❌ Failed to download for PO {po_number}: {e}")

        # Now scroll and download any new rows that appear
        print("🔽 Scrolling to load and download remaining rows...")
        new_downloads = await scroll_and_gather_new_downloads(page, scroll_container_selector, already_downloaded_pos)
        print(f"Found {len(new_downloads)} new rows after scrolling.")
        for idx, (po_number, download_icon) in enumerate(new_downloads, 1):
            print(f"➡️ Downloading for PO (scrolled): {po_number} ...")
            try:
                async with page.expect_download() as download_info:
                    await download_icon.click(force=True)
                download = await download_info.value
                target_file = DOWNLOAD_DIR / f"{po_number}.zip"
                await download.save_as(str(target_file))
                print(f"✅ Saved file to {target_file}")
                extract_pdfs(target_file, PDF_DIR)
                print(f"📄 Extracted PDFs from {target_file} to {PDF_DIR}")
            except Exception as e:
                print(f"❌ Failed to download for PO {po_number}: {e}")

        print(f"🎉 Done! All files downloaded. All PDFs are in {PDF_DIR}")

if __name__ == "__main__":
    asyncio.run(main())