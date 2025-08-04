import requests
import json
import pandas as pd
from datetime import datetime

jwt_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWQiOiJmYjYzMDZiMy1jYmMxLTQxODEtYmYyMS1lNGM0Y2YwMDUzODUiLCJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6IkRlZmF1bHQiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbIkRlZmF1bHQiXX0sImVtYWlsSWQiOiJvcGVyYXRpb25zQHNhbmZlLmluIiwic2Vzc2lvbklkIjoiNzQ0M2ZiNGYtMDdjZi00NDQxLTg0ZDgtNDIwNTZiZjJmNzJjLTE3NTMzNDgyOTkwNjYiLCJ1c2VySWQiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWRzIjpbXSwicm9sZU5hbWUiOiJFeHRlcm5hbCBTdXBlciBBZHMgQWRtaW4iLCJhcHBsaWNhdGlvbklkIjoiZDBjZDQ4NzMtN2NiMy00YzdjLTlhMjUtM2IxMDlhMGQyMzAxIiwiY2F0ZWdvcnkiOiJFeHRlcm5hbCIsImV4cCI6MTc1MzM4MTc5OSwicm9sZU5hbWVzIjpbXSwiaWF0IjoxNzUzMzQ4Mjk5fQ.d2QpInglHJjB9kec2YNc8XDFlqxPcitnYDgjQYa0A_8"  # Replace with your actual token
vendor_name = "Sanfe"  # Change if needed

def fetch_all_invoices():
    url = "https://fcc.zepto.co.in/api/v1/payment/invoice/filter"
    limit = 100  # Maximum allowed per API docs
    offset = 0
    all_invoices = []

    # Set the date range for 1 April 2024 to 31 March 2025
    start_date = "2024-04-01T00:00:00.000Z"
    end_date   = "2025-03-31T23:59:59.999Z"

    while True:
        payload = json.dumps({
            "startDate": start_date,
            "endDate": end_date,
            "offset": offset,
            "limit": limit,
            "statusList": [],
            "refNos": [],
            "poNos": [],
            "asnNos": [],
            "invoiceNos": [],
            "vendorCodes": []
        })
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': jwt_token,
            'content-type': 'application/json',
            'origin': 'https://brands.zepto.co.in',
            'priority': 'u=1, i',
            'referer': 'https://brands.zepto.co.in/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-proxy-target': 'brand-analytics'
        }

        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            invoice_list = data.get('data', {}).get('invoiceList', [])
            all_invoices.extend(invoice_list)
            has_next = data.get('data', {}).get('hasNext', False)
            if has_next and len(invoice_list) > 0:
                offset += limit
                print(f"Fetched {len(invoice_list)} invoices, continuing...")
            else:
                print("No more invoices to fetch.")
                break
        else:
            print(f"Failed to fetch invoices: {response.status_code} - {response.text}")
            break

    # Save all invoices to Excel
    if all_invoices:
        df = pd.DataFrame(all_invoices)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{vendor_name}_{timestamp}_invoice_apr2024_mar2025.xlsx"
        df.to_excel(filename, index=False)
        print(f"Saved {len(all_invoices)} invoices to {filename}")
    else:
        print("No invoices found for vendor.")

fetch_all_invoices()