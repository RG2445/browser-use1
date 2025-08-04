import requests
import json
import pandas as pd
from datetime import datetime

jwt_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWQiOiJmYjYzMDZiMy1jYmMxLTQxODEtYmYyMS1lNGM0Y2YwMDUzODUiLCJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6IkRlZmF1bHQiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbIkRlZmF1bHQiXX0sImVtYWlsSWQiOiJvcGVyYXRpb25zQHNhbmZlLmluIiwic2Vzc2lvbklkIjoiNzQ0M2ZiNGYtMDdjZi00NDQxLTg0ZDgtNDIwNTZiZjJmNzJjLTE3NTMzNDgyOTkwNjYiLCJ1c2VySWQiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWRzIjpbXSwicm9sZU5hbWUiOiJFeHRlcm5hbCBTdXBlciBBZHMgQWRtaW4iLCJhcHBsaWNhdGlvbklkIjoiZDBjZDQ4NzMtN2NiMy00YzdjLTlhMjUtM2IxMDlhMGQyMzAxIiwiY2F0ZWdvcnkiOiJFeHRlcm5hbCIsImV4cCI6MTc1MzM4MTc5OSwicm9sZU5hbWVzIjpbXSwiaWF0IjoxNzUzMzQ4Mjk5fQ.d2QpInglHJjB9kec2YNc8XDFlqxPcitnYDgjQYa0A_8"  # Replace with your actual JWT token
vendor_name = "Sanfe"  # Change to your vendor name if needed

def fetch_all_payment_advice():
    url = "https://fcc.zepto.co.in/api/v1/payment/payment-advice/filter"
    limit = 100 # As per your payload, max allowed by API
    offset = 0
    all_advices = []

    # Set your date range here
    start_date = "2024-04-01T18:30:00.000Z"
    end_date = "2025-03-31T18:29:59.999Z"

    while True:
        payload = json.dumps({
            "startDate": start_date,
            "endDate": end_date,
            "offset": offset,
            "limit": limit,
            "refNos": [],
            "utrNos": []
        })
        headers = {
            'accept': 'application/json',
            'authorization': jwt_token,
            'content-type': 'application/json',
        }

        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            data = response.json()
            # Adjust the below key according to actual response structure
            advice_list = data.get('data', {}).get('paymentAdviceList', [])
            all_advices.extend(advice_list)
            has_next = data.get('data', {}).get('hasNext', False)
            if has_next and len(advice_list) > 0:
                offset += limit
                print(f"Fetched {len(advice_list)} payment advices, continuing...")
            else:
                print("No more payment advices to fetch.")
                break
        else:
            print(f"Failed to fetch payment advices: {response.status_code} - {response.text}")
            break

    # Save all payment advices to Excel
    if all_advices:
        df = pd.DataFrame(all_advices)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{vendor_name}_{timestamp}_payment_advice.xlsx"
        df.to_excel(filename, index=False)
        print(f"Saved {len(all_advices)} payment advices to {filename}")
    else:
        print("No payment advices found for vendor.")

fetch_all_payment_advice()