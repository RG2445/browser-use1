import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import time

START_DATE = "2024-04-01T00:00:00.000Z"
END_DATE = "2025-03-31T23:59:59.999Z"

class ZeptoDataFetcher:
    def __init__(self, jwt_token: str, vendor_name: str = "Pilgrims"):
        self.jwt_token = jwt_token
        self.vendor_name = vendor_name
        self.base_headers = {
            'accept': 'application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': self.jwt_token,
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
    
    def get_date_chunks(self, start_date_str, end_date_str, days_per_chunk=90):
        start_date = datetime.strptime(start_date_str.split('T')[0], "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str.split('T')[0], "%Y-%m-%d")
        chunks = []
        current_start = start_date
        while current_start <= end_date:
            chunk_end = min(current_start + timedelta(days=days_per_chunk-1), end_date)
            chunk_start_str = current_start.strftime("%Y-%m-%dT00:00:00.000Z")
            chunk_end_str = chunk_end.strftime("%Y-%m-%dT23:59:59.999Z")
            chunks.append((chunk_start_str, chunk_end_str))
            current_start = chunk_end + timedelta(days=1)
        return chunks

    def fetch_all_invoices(self):
        print("=" * 50)
        print("FETCHING INVOICES")
        print("=" * 50)
        url = "https://fcc.zepto.co.in/api/v1/payment/invoice/filter"
        limit = 100
        offset = 0
        all_invoices = []
        start_date = START_DATE
        end_date = END_DATE
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
            try:
                response = requests.post(url, headers=self.base_headers, data=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    invoice_list = data.get('data', {}).get('invoiceList', [])
                    all_invoices.extend(invoice_list)
                    has_next = data.get('data', {}).get('hasNext', False)
                    if has_next and len(invoice_list) > 0:
                        offset += limit
                        print(f"Fetched {len(invoice_list)} invoices, total so far: {len(all_invoices)}")
                    else:
                        print(f"Finished fetching invoices. Total: {len(all_invoices)}")
                        break
                else:
                    print(f"Failed to fetch invoices: {response.status_code} - {response.text}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Request failed for invoices: {e}")
                break
        return all_invoices

    def fetch_all_settlements(self):
        print("=" * 50)
        print("FETCHING SETTLEMENTS (DN/CN)")
        print("=" * 50)
        url = "https://fcc.zepto.co.in/api/v1/payment/settlement/filter"
        limit = 100
        offset = 0
        all_settlements = []
        start_date = START_DATE
        end_date = END_DATE
        while True:
            payload = json.dumps({
                "startDate": start_date,
                "endDate": end_date,
                "offset": offset,
                "limit": limit,
                "refNos": [],
                "settlementSubTypes": []
            })
            try:
                response = requests.post(url, headers=self.base_headers, data=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    settlement_list = data.get('data', {}).get('settlements', [])
                    all_settlements.extend(settlement_list)
                    has_next = data.get('data', {}).get('hasNext', False)
                    if has_next and len(settlement_list) > 0:
                        offset += limit
                        print(f"Fetched {len(settlement_list)} settlements, total so far: {len(all_settlements)}")
                    else:
                        print(f"Finished fetching settlements. Total: {len(all_settlements)}")
                        break
                else:
                    print(f"Failed to fetch settlements: {response.status_code} - {response.text}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Request failed for settlements: {e}")
                break
        return all_settlements

    def fetch_all_payment_advice(self):
        print("=" * 50)
        print("FETCHING PAYMENT ADVICE")
        print("=" * 50)
        url = "https://fcc.zepto.co.in/api/v1/payment/payment-advice/filter"
        limit = 100
        offset = 0
        all_advices = []
        start_date = START_DATE
        end_date = END_DATE
        while True:
            payload = json.dumps({
                "startDate": start_date,
                "endDate": end_date,
                "offset": offset,
                "limit": limit,
                "refNos": [],
                "utrNos": []
            })
            try:
                response = requests.post(url, headers=self.base_headers, data=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    advice_list = data.get('data', {}).get('paymentAdviceList', [])
                    all_advices.extend(advice_list)
                    has_next = data.get('data', {}).get('hasNext', False)
                    if has_next and len(advice_list) > 0:
                        offset += limit
                        print(f"Fetched {len(advice_list)} payment advices, total so far: {len(all_advices)}")
                    else:
                        print(f"Finished fetching payment advice. Total: {len(all_advices)}")
                        break
                else:
                    print(f"Failed to fetch payment advices: {response.status_code} - {response.text}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Request failed for payment advice: {e}")
                break
        return all_advices

    def fetch_all_grns(self):
        print("=" * 50)
        print("FETCHING GRNs (in 90-day chunks)")
        print("=" * 50)
        url = "https://fcc.zepto.co.in/api/v1/grn/filter"
        limit = 100
        all_grns = []
        date_chunks = self.get_date_chunks(START_DATE, END_DATE, 90)
        print(f"Breaking down date range into {len(date_chunks)} chunks of 90 days each:")
        for i, (chunk_start, chunk_end) in enumerate(date_chunks):
            print(f"  Chunk {i+1}: {chunk_start.split('T')[0]} to {chunk_end.split('T')[0]}")
        for chunk_index, (chunk_start_date, chunk_end_date) in enumerate(date_chunks):
            print("\n" + "=" * 30)
            print(f"PROCESSING GRN CHUNK {chunk_index+1}/{len(date_chunks)}")
            print(f"Date range: {chunk_start_date.split('T')[0]} to {chunk_end_date.split('T')[0]}")
            print("=" * 30)
            offset = 0
            chunk_grns = []
            while True:
                payload = json.dumps({
                    "grnStartDate": chunk_start_date,
                    "grnEndDate": chunk_end_date,
                    "offset": offset,
                    "limit": limit,
                    "vendorCodes": [],
                    "locationCodes": [],
                    "statusList": [],
                    "grnNos": [],
                    "poIds": []
                })
                try:
                    response = requests.post(url, headers=self.base_headers, data=payload, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        grn_list = data.get('data', {}).get('grnList', [])
                        chunk_grns.extend(grn_list)
                        has_next = data.get('data', {}).get('hasNext', False)
                        if has_next and len(grn_list) > 0:
                            offset += limit
                            print(f"Fetched {len(grn_list)} GRNs, total in chunk: {len(chunk_grns)}")
                        else:
                            print(f"Finished fetching GRNs for chunk {chunk_index+1}. Total in chunk: {len(chunk_grns)}")
                            all_grns.extend(chunk_grns)
                            break
                    else:
                        print(f"Failed to fetch GRNs for chunk {chunk_index+1}: {response.status_code} - {response.text}")
                        break
                except requests.exceptions.RequestException as e:
                    print(f"Request failed for GRNs chunk {chunk_index+1}: {e}")
                    break
                time.sleep(1)
            if chunk_index < len(date_chunks) - 1:
                print(f"Waiting 3 seconds before processing next chunk...")
                time.sleep(3)
        print(f"Finished fetching all GRNs across {len(date_chunks)} chunks. Total GRNs: {len(all_grns)}")
        return all_grns

    def fetch_all_grn_details(self):
        print("=" * 50)
        print("FETCHING GRN DETAILS")
        print("=" * 50)
        grns = self.fetch_all_grns()
        all_grn_details = []
        if not grns:
            print("No GRNs found to fetch details for.")
            return all_grn_details
        print(f"Found {len(grns)} GRNs to fetch details for")
        for i, grn in enumerate(grns):
            grn_no = grn.get("grnNo")
            if grn_no:
                print(f"Fetching details for GRN: {grn_no} ({i+1}/{len(grns)})")
                url = f"https://fcc.zepto.co.in/api/v1/grn/{grn_no}"
                try:
                    response = requests.get(url, headers=self.base_headers, timeout=30)
                    if response.status_code == 200:
                        grn_detail = response.json().get('data', {})
                        all_grn_details.append(grn_detail)
                    else:
                        print(f"Failed to fetch details for GRN {grn_no}: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"Request failed for GRN details {grn_no}: {e}")
                time.sleep(0.5)
                if (i + 1) % 10 == 0:
                    print(f"Progress: {i+1}/{len(grns)} GRNs processed ({((i+1)/len(grns))*100:.1f}%)")
        print(f"Finished fetching details for {len(all_grn_details)} GRNs.")
        return all_grn_details

    def fetch_payment_advice_logs(self):
        print("=" * 50)
        print("FETCHING PAYMENT ADVICE LOGS")
        print("=" * 50)
        payment_advices = self.fetch_all_payment_advice()
        all_logs_data = []
        if not payment_advices:
            print("No payment advices found to fetch logs for.")
            return all_logs_data
        for i, payment_advice in enumerate(payment_advices):
            payment_advice_id = payment_advice.get("id")
            if payment_advice_id:
                print(f"Fetching logs for Payment Advice ID: {payment_advice_id} ({i+1}/{len(payment_advices)})")
                url = f"https://fcc.zepto.co.in/api/v1/payment/payment-advice/{payment_advice_id}"
                try:
                    response = requests.get(url, headers=self.base_headers, timeout=30)
                    if response.status_code == 200:
                        payment_advice_detail = response.json().get('data', {})
                        ref_no = payment_advice_detail.get("referenceNo")
                        logs = payment_advice_detail.get("paymentAdviceLogs") or []
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
                        print(f"Failed to fetch logs for Payment Advice ID {payment_advice_id}: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"Request failed for Payment Advice logs {payment_advice_id}: {e}")
                time.sleep(0.5)
        print(f"Finished fetching logs for {len(all_logs_data)} payment advice records.")
        return all_logs_data

    def fetch_all_returns(self):
        print("=" * 50)
        print("FETCHING RETURNS/RTVs (in 90-day chunks)")
        print("=" * 50)
        url = "https://fcc.zepto.co.in/api/v1/rtv/filter"
        limit = 100
        all_returns = []
        date_chunks = self.get_date_chunks(START_DATE, END_DATE, 90)
        print(f"Breaking down date range into {len(date_chunks)} chunks of 90 days each:")
        for i, (chunk_start, chunk_end) in enumerate(date_chunks):
            print(f"  Chunk {i+1}: {chunk_start.split('T')[0]} to {chunk_end.split('T')[0]}")
        for chunk_index, (chunk_start_date, chunk_end_date) in enumerate(date_chunks):
            print("\n" + "=" * 30)
            print(f"PROCESSING RTV CHUNK {chunk_index+1}/{len(date_chunks)}")
            print(f"Date range: {chunk_start_date.split('T')[0]} to {chunk_end_date.split('T')[0]}")
            print("=" * 30)
            offset = 0
            chunk_returns = []
            while True:
                payload = json.dumps({
                    "creationStartDate": chunk_start_date,
                    "creationEndDate": chunk_end_date,
                    "offset": offset,
                    "limit": limit,
                    "locationCodes": [],
                    "vendorCodes": [],
                    "referenceNos": [],
                    "statusList": [],
                    "poIds": [],
                    "returnOrderStartDate": None,
                    "returnOrderEndDate": None
                })
                try:
                    response = requests.post(url, headers=self.base_headers, data=payload, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        rtv_list = data.get('data', {}).get('rtvList', [])
                        if rtv_list:
                            chunk_returns.extend(rtv_list)
                        has_next = data.get('data', {}).get('hasNext', False)
                        if has_next and rtv_list:
                            offset += limit
                            print(f"Fetched {len(rtv_list)} RTVs, total in chunk: {len(chunk_returns)}")
                        else:
                            print(f"Finished fetching RTVs for chunk {chunk_index+1}. Total in chunk: {len(chunk_returns)}")
                            all_returns.extend(chunk_returns)
                            break
                    else:
                        print(f"Failed to fetch RTVs for chunk {chunk_index+1}: {response.status_code} - {response.text}")
                        break
                except requests.exceptions.RequestException as e:
                    print(f"Request failed for RTVs chunk {chunk_index+1}: {e}")
                    break
                time.sleep(1)
            if chunk_index < len(date_chunks) - 1:
                print(f"Waiting 3 seconds before processing next chunk...")
                time.sleep(3)
        print(f"Finished fetching all RTVs across {len(date_chunks)} chunks. Total RTVs: {len(all_returns)}")
        return all_returns

    def save_all_data_to_excel(self, invoices, settlements, payment_advice, grns, grn_details, payment_advice_logs, returns):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.vendor_name}_{timestamp}_complete_data.xlsx"
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                if invoices:
                    df_invoices = pd.DataFrame(invoices)
                    df_invoices.to_excel(writer, sheet_name='Invoices', index=False)
                    print(f"Added {len(invoices)} invoices to 'Invoices' sheet")
                else:
                    pd.DataFrame({'Message': ['No invoice data found']}).to_excel(
                        writer, sheet_name='Invoices', index=False)
                    print("No invoices found - created empty 'Invoices' sheet")
                if settlements:
                    df_settlements = pd.DataFrame(settlements)
                    df_settlements.to_excel(writer, sheet_name='DN_CN', index=False)
                    print(f"Added {len(settlements)} settlements to 'DN_CN' sheet")
                else:
                    pd.DataFrame({'Message': ['No settlement data found']}).to_excel(
                        writer, sheet_name='DN_CN', index=False)
                    print("No settlements found - created empty 'DN_CN' sheet")
                if payment_advice:
                    df_payment_advice = pd.DataFrame(payment_advice)
                    df_payment_advice.to_excel(writer, sheet_name='Payment_Advice', index=False)
                    print(f"Added {len(payment_advice)} payment advices to 'Payment_Advice' sheet")
                else:
                    pd.DataFrame({'Message': ['No payment advice data found']}).to_excel(
                        writer, sheet_name='Payment_Advice', index=False)
                    print("No payment advice found - created empty 'Payment_Advice' sheet")
                if grns:
                    df_grns = pd.DataFrame(grns)
                    df_grns.to_excel(writer, sheet_name='GRNs', index=False)
                    print(f"Added {len(grns)} GRNs to 'GRNs' sheet")
                else:
                    pd.DataFrame({'Message': ['No GRN data found']}).to_excel(
                        writer, sheet_name='GRNs', index=False)
                    print("No GRNs found - created empty 'GRNs' sheet")
                if grn_details:
                    df_grn_details = pd.DataFrame(grn_details)
                    df_grn_details.to_excel(writer, sheet_name='GRN_Details', index=False)
                    print(f"Added {len(grn_details)} GRN details to 'GRN_Details' sheet")
                else:
                    pd.DataFrame({'Message': ['No GRN details data found']}).to_excel(
                        writer, sheet_name='GRN_Details', index=False)
                    print("No GRN details found - created empty 'GRN_Details' sheet")
                if payment_advice_logs:
                    df_payment_advice_logs = pd.DataFrame(payment_advice_logs)
                    df_payment_advice_logs.to_excel(writer, sheet_name='Payment_Advice_Logs', index=False)
                    print(f"Added {len(payment_advice_logs)} payment advice logs to 'Payment_Advice_Logs' sheet")
                else:
                    pd.DataFrame({'Message': ['No payment advice logs data found']}).to_excel(
                        writer, sheet_name='Payment_Advice_Logs', index=False)
                    print("No payment advice logs found - created empty 'Payment_Advice_Logs' sheet")
                if returns:
                    df_returns = pd.DataFrame(returns)
                    df_returns.to_excel(writer, sheet_name='Returns_RTV', index=False)
                    print(f"Added {len(returns)} RTVs to 'Returns_RTV' sheet")
                else:
                    pd.DataFrame({'Message': ['No RTV (returns) data found']}).to_excel(
                        writer, sheet_name='Returns_RTV', index=False)
                    print("No RTVs found - created empty 'Returns_RTV' sheet")
            print("=" * 50)
            print(f"SUCCESS! All data saved to: {filename}")
            print("=" * 50)
            print("File contains the following sheets:")
            print("1. Invoices - All invoice data")
            print("2. DN_CN - All settlement data (Debit/Credit Notes)")
            print("3. Payment_Advice - All payment advice data")
            print("4. GRNs - All GRN (Goods Received Note) data")
            print("5. GRN_Details - Detailed information for each GRN")
            print("6. Payment_Advice_Logs - Payment advice log entries")
            print("7. Returns_RTV - Return to Vendor data")
            return filename
        except Exception as e:
            print(f"Failed to save data to Excel: {e}")
            return None

    def fetch_and_save_all_data(self):
        print("Starting data fetch for Zepto Vendor Portal")
        print(f"Vendor: {self.vendor_name}")
        print(f"Date Range: {START_DATE[:10]} to {END_DATE[:10]}")
        print("=" * 50)
        invoices = self.fetch_all_invoices()
        settlements = self.fetch_all_settlements()
        payment_advice = self.fetch_all_payment_advice()
        grns = self.fetch_all_grns()
        grn_details = self.fetch_all_grn_details()
        payment_advice_logs = self.fetch_payment_advice_logs()
        returns = self.fetch_all_returns()
        filename = self.save_all_data_to_excel(
            invoices, settlements, payment_advice,
            grns, grn_details, payment_advice_logs, returns
        )
        if filename:
            print(f"\n✅ Data extraction completed successfully!")
            print(f"📁 File saved as: {filename}")
            print(f"📊 Summary:")
            print(f"   - Invoices: {len(invoices)} records")
            print(f"   - Settlements (DN/CN): {len(settlements)} records")
            print(f"   - Payment Advice: {len(payment_advice)} records")
            print(f"   - GRNs: {len(grns)} records")
            print(f"   - GRN Details: {len(grn_details)} records")
            print(f"   - Payment Advice Logs: {len(payment_advice_logs)} records")
            print(f"   - Returns (RTVs): {len(returns)} records")
        else:
            print("❌ Failed to save data to Excel file")

def main():
    jwt_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI3ODJlMjM5Yi1hMTJiLTQ0ZDItYjhlNS1iZTJmOGU2NWVhMzIiLCJyb2xlSWQiOiJmYjYzMDZiMy1jYmMxLTQxODEtYmYyMS1lNGM0Y2YwMDUzODUiLCJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6IkRlZmF1bHQiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbIkRlZmF1bHQiXX0sImVtYWlsSWQiOiJwcmVtbmF0aC5zaGluZGVAZGlzY292ZXJwaWxncmltLmNvbSIsInNlc3Npb25JZCI6ImRiNDU0Mjg4LTUyMDAtNGMzOS05MWEzLTU3NjA2NTYyZmQxZi0xNzUzNjgzNjk5OTY1IiwidXNlcklkIjoiNzgyZTIzOWItYTEyYi00NGQyLWI4ZTUtYmUyZjhlNjVlYTMyIiwicm9sZUlkcyI6W10sInJvbGVOYW1lIjoiRXh0ZXJuYWwgU3VwZXIgQWRzIEFkbWluIiwiYXBwbGljYXRpb25JZCI6ImQwY2Q0ODczLTdjYjMtNGM3Yy05YTI1LTNiMTA5YTBkMjMwMSIsImNhdGVnb3J5IjoiRXh0ZXJuYWwiLCJleHAiOjE3NTM3MjczOTksInJvbGVOYW1lcyI6W10sImlhdCI6MTc1MzY4MzY5OX0.p-zRs0bVfwDLQjCW1LeWhBATesxvF9fAwxg3qxR7E7k"
    vendor_name = "Pilgrims"
    fetcher = ZeptoDataFetcher(jwt_token, vendor_name)
    fetcher.fetch_and_save_all_data()

if __name__ == "__main__":
    main()