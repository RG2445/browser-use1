import requests
import json
import pandas as pd
from datetime import datetime

# Token provided by the user
jwt_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWQiOiJmYjYzMDZiMy1jYmMxLTQxODEtYmYyMS1lNGM0Y2YwMDUzODUiLCJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6IkRlZmF1bHQiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbIkRlZmF1bHQiXX0sImVtYWlsSWQiOiJvcGVyYXRpb25zQHNhbmZlLmluIiwic2Vzc2lvbklkIjoiM2QwNGZkYWQtYzJmYy00YzFmLTk0ODctMzNlMGY4MmM2NjAwLTE3NTM1MTA4MjIyMTYiLCJ1c2VySWQiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWRzIjpbXSwicm9sZU5hbWUiOiJFeHRlcm5hbCBTdXBlciBBZHMgQWRtaW4iLCJhcHBsaWNhdGlvbklkIjoiZDBjZDQ4NzMtN2NiMy00YzdjLTlhMjUtM2IxMDlhMGQyMzAxIiwiY2F0ZWdvcnkiOiJFeHRlcm5hbCIsImV4cCI6MTc1MzU1NDU5OSwicm9sZU5hbWVzIjpbXSwiaWF0IjoxNzUzNTEwODIyfQ.HhGTETAM359-q_iLwrkIKcP2pnFRbBGvbVLJGYh7ocI"
vendor_name = "Sanfe"  # Change if needed

def fetch_payment_advice_logs():
    base_url = "https://fcc.zepto.co.in/api/v1/payment/payment-advice"
    list_url = f"{base_url}/filter"
    limit = 19
    offset = 0
    all_logs_data = []

    start_date = "2024-04-01T18:30:00.000Z"
    end_date = "2025-03-31T18:29:59.999Z"

    # Step 1: Fetch the list of payment advices
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
            'content-type': 'application/json'
        }

        response = requests.post(list_url, headers=headers, data=payload)
        print(f"Status Code (List API): {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            payment_advice_list = data.get('data', {}).get('paymentAdviceList', [])

            # Step 2: Fetch logs for each Payment Advice (id)
            for payment_advice in payment_advice_list:
                payment_advice_id = payment_advice.get("id")  # Use 'id' for details
                if payment_advice_id:
                    detail_url = f"{base_url}/{payment_advice_id}"
                    detail_response = requests.get(detail_url, headers=headers)
                    print(f"Fetching details for Payment Advice ID: {payment_advice_id} - Status Code: {detail_response.status_code}")

                    if detail_response.status_code == 200:
                        payment_advice_detail = detail_response.json().get('data', {})
                        ref_no = payment_advice_detail.get("referenceNo")
                        logs = payment_advice_detail.get("paymentAdviceLogs", [])
                        for log in logs:
                            flattened_log = {
                                "Reference No": ref_no,
                                "Log ID": log.get("id"),
                                "Booking Date": log.get("bookingDate"),
                                "Posting Date": log.get("postingDate"),
                                "Settlement Type": log.get("settlementType"),
                                "Type": log.get("type"),
                                "Amount": log.get("amount"),
                                "TDS": log.get("tds"),
                                "Payment Amount": log.get("paymentAmount"),
                                "External Reference No": log.get("extReferenceNo"),
                            }
                            all_logs_data.append(flattened_log)
                    else:
                        print(f"Failed to fetch details for Payment Advice ID {payment_advice_id}: {detail_response.status_code} - {detail_response.text}")

            # Pagination handling
            if len(payment_advice_list) == limit:
                offset += limit
                print(f"Fetched {len(payment_advice_list)} Payment Advice records, continuing...")
            else:
                print("No more Payment Advice records to fetch.")
                break
        else:
            print(f"Failed to fetch Payment Advice list: {response.status_code} - {response.text}")
            break

    # Step 3: Save all Payment Advice logs to Excel
    if all_logs_data:
        df = pd.DataFrame(all_logs_data)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{vendor_name}_{timestamp}_payment_advice_logs.xlsx"
        df.to_excel(filename, index=False)
        print(f"Saved {len(all_logs_data)} Payment Advice logs to {filename}")
    else:
        print("No Payment Advice logs found.")

fetch_payment_advice_logs()