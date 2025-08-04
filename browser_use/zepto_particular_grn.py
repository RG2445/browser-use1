import requests
import json
import pandas as pd
from datetime import datetime

jwt_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWQiOiJmYjYzMDZiMy1jYmMxLTQxODEtYmYyMS1lNGM0Y2YwMDUzODUiLCJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6IkRlZmF1bHQiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbIkRlZmF1bHQiXX0sImVtYWlsSWQiOiJvcGVyYXRpb25zQHNhbmZlLmluIiwic2Vzc2lvbklkIjoiNTJkNTJhNmYtYWU2NS00OGFlLWE0MDItMGJiYTVkZGRiNjVlLTE3NTM0MjQwNjIyNjAiLCJ1c2VySWQiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWRzIjpbXSwicm9sZU5hbWUiOiJFeHRlcm5hbCBTdXBlciBBZHMgQWRtaW4iLCJhcHBsaWNhdGlvbklkIjoiZDBjZDQ4NzMtN2NiMy00YzdjLTlhMjUtM2IxMDlhMGQyMzAxIiwiY2F0ZWdvcnkiOiJFeHRlcm5hbCIsImV4cCI6MTc1MzQ2ODE5OSwicm9sZU5hbWVzIjpbXSwiaWF0IjoxNzUzNDI0MDYyfQ.MLCvKsnCshxNlEZ0PvtlScMocpBDGCQs6cKrNO_WAhA"  # Replace with your actual token
vendor_name = "Sanfe"  # Change if needed

def fetch_all_grn_details():
    base_url = "https://fcc.zepto.co.in/api/v1/grn"
    list_url = f"{base_url}/filter"
    limit = 100
    offset = 0
    all_grn_details = []

    grn_start_date = "2025-06-24T18:30:00.000Z"
    grn_end_date = "2025-07-24T18:29:59.999Z"

    # Step 1: Fetch the list of GRNs
    while True:
        payload = json.dumps({
            "grnStartDate": grn_start_date,
            "grnEndDate": grn_end_date,
            "offset": offset,
            "limit": limit,
            "vendorCodes": [],
            "locationCodes": [],
            "statusList": [],
            "grnNos": [],
            "poIds": []
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
            grn_list = data.get('data', {}).get('grnList', [])

            # Step 2: Fetch details for each GRN ID
            for grn in grn_list:
                grn_no = grn.get("grnNo")
                if grn_no:
                    detail_url = f"{base_url}/{grn_no}"
                    detail_response = requests.get(detail_url, headers=headers)
                    print(f"Fetching details for GRN: {grn_no} - Status Code: {detail_response.status_code}")

                    if detail_response.status_code == 200:
                        grn_detail = detail_response.json().get('data', {})
                        all_grn_details.append(grn_detail)
                    else:
                        print(f"Failed to fetch details for GRN {grn_no}: {detail_response.status_code} - {detail_response.text}")

            # Pagination handling
            if len(grn_list) == limit:
                offset += limit
                print(f"Fetched {len(grn_list)} GRNs from list, continuing...")
            else:
                print("No more GRNs to fetch from list.")
                break
        else:
            print(f"Failed to fetch GRN list: {response.status_code} - {response.text}")
            break

    # Step 3: Save all GRN details to Excel
    if all_grn_details:
        df = pd.DataFrame(all_grn_details)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{vendor_name}_{timestamp}_grn_details.xlsx"
        df.to_excel(filename, index=False)
        print(f"Saved {len(all_grn_details)} GRN details to {filename}")
    else:
        print("No GRN details found.")

fetch_all_grn_details()