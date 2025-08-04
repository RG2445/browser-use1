import requests
import json
import pandas as pd
from datetime import datetime

jwt_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWQiOiJmYjYzMDZiMy1jYmMxLTQxODEtYmYyMS1lNGM0Y2YwMDUzODUiLCJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6IkRlZmF1bHQiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbIkRlZmF1bHQiXX0sImVtYWlsSWQiOiJvcGVyYXRpb25zQHNhbmZlLmluIiwic2Vzc2lvbklkIjoiNTJkNTJhNmYtYWU2NS00OGFlLWE0MDItMGJiYTVkZGRiNjVlLTE3NTM0MjQwNjIyNjAiLCJ1c2VySWQiOiJmNDA1MThiMi0wMzE3LTQ4ZGQtOGMwYy04NTczNmI1YTRhNzMiLCJyb2xlSWRzIjpbXSwicm9sZU5hbWUiOiJFeHRlcm5hbCBTdXBlciBBZHMgQWRtaW4iLCJhcHBsaWNhdGlvbklkIjoiZDBjZDQ4NzMtN2NiMy00YzdjLTlhMjUtM2IxMDlhMGQyMzAxIiwiY2F0ZWdvcnkiOiJFeHRlcm5hbCIsImV4cCI6MTc1MzQ2ODE5OSwicm9sZU5hbWVzIjpbXSwiaWF0IjoxNzUzNDI0MDYyfQ.MLCvKsnCshxNlEZ0PvtlScMocpBDGCQs6cKrNO_WAhA"  # Replace with your actual token
vendor_name = "Sanfe" 

def fetch_all_grns():
    url = "https://fcc.zepto.co.in/api/v1/grn/filter"
    limit = 100
    offset = 0
    all_grns = []

    grn_start_date = "2025-06-24T18:30:00.000Z"
    grn_end_date = "2025-07-24T18:29:59.999Z"

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

        response = requests.post(url, headers=headers, data=payload)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            grn_list = data.get('data', {}).get('grnList', [])
            all_grns.extend(grn_list)

            if len(grn_list) == limit:  
                offset += limit
                print(f"Fetched {len(grn_list)} GRNs, continuing...")
            else:
                print("No more GRNs to fetch.")
                break
        else:
            print(f"Failed to fetch GRNs: {response.status_code} - {response.text}")
            break

    if all_grns:
        df = pd.DataFrame(all_grns)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{vendor_name}_{timestamp}_grns_20250624_20250724.xlsx"
        df.to_excel(filename, index=False)
        print(f"Saved {len(all_grns)} GRNs to {filename}")
    else:
        print("No GRNs found for vendor.")

fetch_all_grns()