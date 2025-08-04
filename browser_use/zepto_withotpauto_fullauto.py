import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import re
import base64
from typing import Optional, Dict, Any, List, Union

class CompleteZeptoAutomation:
    def __init__(self, vendor_name: str = "Sanfe"):
        self.vendor_name = vendor_name
        self.jwt_token: Optional[str] = None
        self.session = requests.Session()
        self.base_url = "https://fcc.zepto.co.in"
        self.login_url = "https://brands.zepto.co.in"
        self.login_session_data: Dict[str, Any] = {}
        
        # Standard headers for all requests
        self.base_headers = {
            'accept': 'application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://brands.zepto.co.in',
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
    
    def complete_login_flow(self, email: str, password: str, n8n_webhook_url: str) -> bool:
        """Complete login flow: credentials -> OTP via n8n -> JWT extraction"""
        print("🚀 Starting complete login automation...")
        print(f"📧 Email: {email}")
        print(f"🕐 Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"👤 User: RG2445-Nakad")
        print("=" * 60)
        
        # Step 1: Send login credentials
        if not self.send_login_credentials(email, password):
            return False
        
        # Step 2: Get OTP via n8n
        otp = self.get_otp_via_n8n(n8n_webhook_url, email)
        if not otp:
            return False
        
        # Step 3: Verify OTP and get JWT token
        if not self.verify_otp_and_extract_jwt(otp, email):
            return False
        
        print("✅ Complete login flow successful!")
        if self.jwt_token:
            print(f"🔑 JWT Token obtained: {self.jwt_token[:50]}...")
        return True
    
    def send_login_credentials(self, email: str, password: str) -> bool:
        """Step 1: Send login credentials to Zepto"""
        print("🔐 Step 1: Sending login credentials...")
        
        try:
            # First get the login page to establish session
            login_page = self.session.get(f"{self.login_url}/login", timeout=30)
            print(f"✅ Login page accessed: {login_page.status_code}")
            
            # Try multiple possible login endpoints
            login_endpoints = [
                f"{self.base_url}/api/v1/auth/login",
                f"{self.base_url}/api/auth/login",
                f"{self.login_url}/api/v1/auth/login",
                f"{self.login_url}/api/auth/login"
            ]
            
            # Prepare login payload variations
            login_payloads = [
                {"email": email, "password": password},
                {"emailId": email, "password": password},
                {"username": email, "password": password},
                {"email": email, "password": password, "rememberMe": True}
            ]
            
            # Try different combinations
            for endpoint in login_endpoints:
                for payload in login_payloads:
                    try:
                        print(f"🔄 Trying endpoint: {endpoint}")
                        
                        login_response = self.session.post(
                            endpoint,
                            json=payload,
                            headers=self.base_headers,
                            timeout=30
                        )
                        
                        print(f"📡 Login response: {login_response.status_code}")
                        
                        if login_response.status_code == 200:
                            login_data = login_response.json()
                            print("✅ Login credentials accepted")
                            
                            # Store session data
                            self.login_session_data = login_data if login_data else {}
                            print(f"📄 Response keys: {list(self.login_session_data.keys())}")
                            return True
                            
                        elif login_response.status_code == 400:
                            try:
                                response_data = login_response.json()
                                response_text = json.dumps(response_data)
                            except:
                                response_text = login_response.text
                            
                            if "otp" in response_text.lower() or "verification" in response_text.lower():
                                print("✅ Login successful - OTP required")
                                try:
                                    self.login_session_data = login_response.json()
                                except:
                                    self.login_session_data = {}
                                return True
                            
                    except Exception as e:
                        print(f"⚠️  Endpoint {endpoint} failed: {e}")
                        continue
            
            print("❌ All login attempts failed")
            return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_otp_via_n8n(self, n8n_webhook_url: str, email: str, timeout: int = 180) -> Optional[str]:
        """Step 2: Get OTP via n8n workflow"""
        print("📱 Step 2: Getting OTP via n8n...")
        
        try:
            # Trigger n8n workflow for OTP
            n8n_payload = {
                "action": "get_zepto_otp",
                "email": email,
                "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "vendor": self.vendor_name,
                "user": "RG2445-Nakad"
            }
            
            print("📡 Triggering n8n workflow...")
            print(f"🔗 Webhook URL: {n8n_webhook_url}")
            
            n8n_response = self.session.post(
                n8n_webhook_url,
                json=n8n_payload,
                timeout=30
            )
            
            print(f"📡 n8n Response: {n8n_response.status_code}")
            
            if n8n_response.status_code != 200:
                print(f"❌ n8n trigger failed: {n8n_response.status_code}")
                print(f"Response: {n8n_response.text}")
                return None
            
            print("✅ n8n workflow triggered successfully")
            
            # Check if OTP is returned immediately
            try:
                n8n_result = n8n_response.json()
                if n8n_result and isinstance(n8n_result, dict):
                    print(f"📄 n8n response keys: {list(n8n_result.keys())}")
                    
                    if "otp" in n8n_result and n8n_result["otp"]:
                        otp_value = n8n_result["otp"]
                        print(f"✅ OTP received immediately from n8n: {otp_value}")
                        return str(otp_value)
            except:
                print("📄 n8n response is not JSON or empty")
            
            # If not immediate, poll for OTP
            print("⏳ Waiting for OTP from n8n...")
            return self.poll_n8n_for_otp(n8n_webhook_url, email, timeout)
            
        except Exception as e:
            print(f"❌ n8n error: {e}")
            return None
    
    def poll_n8n_for_otp(self, n8n_webhook_url: str, email: str, timeout: int) -> Optional[str]:
        """Poll n8n for OTP if not immediately available"""
        start_time = time.time()
        poll_count = 0
        
        while time.time() - start_time < timeout:
            poll_count += 1
            print(f"🔄 Polling attempt {poll_count} (timeout in {int(timeout - (time.time() - start_time))}s)...")
            
            try:
                poll_payload = {
                    "action": "check_otp_status",
                    "email": email,
                    "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "user": "RG2445-Nakad"
                }
                
                response = self.session.post(
                    n8n_webhook_url,
                    json=poll_payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        
                        if result and isinstance(result, dict):
                            if "otp" in result and result["otp"]:
                                otp_value = result["otp"]
                                print(f"✅ OTP received after {poll_count} attempts: {otp_value}")
                                return str(otp_value).strip()
                            
                            if "status" in result:
                                print(f"📄 Status: {result['status']}")
                            
                    except:
                        print("📄 Polling response is not JSON")
                
                # Wait before next poll
                time.sleep(12)
                
            except Exception as e:
                print(f"⚠️  Poll error: {e}")
                time.sleep(5)
        
        print("⏰ Timeout waiting for OTP from n8n")
        
        # Fallback: Manual OTP input
        print("🔧 Fallback: Manual OTP input")
        try:
            manual_otp = input("Please enter OTP manually: ").strip()
            if manual_otp and manual_otp.isdigit():
                return manual_otp
        except:
            pass
            
        return None
    
    def verify_otp_and_extract_jwt(self, otp: str, email: str) -> bool:
        """Step 3: Verify OTP and extract JWT token"""
        print(f"🔑 Step 3: Verifying OTP: {otp}")
        
        try:
            # Try multiple OTP verification endpoints
            otp_endpoints = [
                f"{self.base_url}/api/v1/auth/verify-otp",
                f"{self.base_url}/api/auth/verify-otp",
                f"{self.base_url}/api/v1/auth/otp/verify",
                f"{self.login_url}/api/v1/auth/verify-otp"
            ]
            
            # Prepare different OTP payload variations
            base_payloads = [
                {"otp": otp, "email": email},
                {"otp": otp, "emailId": email},
                {"code": otp, "email": email},
                {"verificationCode": otp, "email": email}
            ]
            
            # Add session data if available
            enhanced_payloads = []
            for base_payload in base_payloads:
                payload_copy = base_payload.copy()
                
                if self.login_session_data:
                    session_data = self.login_session_data
                    
                    # Add all possible session fields
                    session_fields = ["sessionId", "tempToken", "verificationId", "requestId", "id"]
                    for field in session_fields:
                        if field in session_data and session_data[field] is not None:
                            payload_copy[field] = session_data[field]
                
                enhanced_payloads.append(payload_copy)
            
            # Try each endpoint with each payload
            for endpoint in otp_endpoints:
                for payload in enhanced_payloads:
                    try:
                        print(f"🔄 Trying OTP endpoint: {endpoint}")
                        
                        otp_response = self.session.post(
                            endpoint,
                            json=payload,
                            headers=self.base_headers,
                            timeout=30
                        )
                        
                        print(f"📡 OTP verification response: {otp_response.status_code}")
                        
                        if otp_response.status_code == 200:
                            try:
                                otp_data = otp_response.json()
                                if otp_data:
                                    print("✅ OTP verification successful")
                                    print(f"📄 OTP response keys: {list(otp_data.keys())}")
                                    
                                    # Extract JWT token from response
                                    if self.extract_jwt_from_response(otp_data, otp_response):
                                        self.validate_jwt_token()
                                        return True
                            except:
                                print("📄 OTP response is not valid JSON")
                        
                    except Exception as e:
                        print(f"⚠️  OTP endpoint {endpoint} failed: {e}")
                        continue
            
            print("❌ All OTP verification attempts failed")
            return False
                
        except Exception as e:
            print(f"❌ OTP verification error: {e}")
            return False
    
    def extract_jwt_from_response(self, response_data: Dict[str, Any], response_obj: requests.Response) -> bool:
        """Extract JWT token from various possible locations"""
        print("🔍 Extracting JWT token...")
        
        # Method 1: Direct token field in response JSON
        token_fields = ["token", "jwt", "authToken", "accessToken", "authorization", "access_token", "auth_token"]
        for field in token_fields:
            if field in response_data and response_data[field]:
                token_value = response_data[field]
                if token_value and isinstance(token_value, str):
                    token = token_value.strip()
                    if token.startswith("eyJ"):
                        self.jwt_token = token
                        print(f"✅ JWT found in response field: {field}")
                        return True
        
        # Method 2: Nested in data object
        if "data" in response_data and isinstance(response_data["data"], dict):
            data = response_data["data"]
            for field in token_fields:
                if field in data and data[field]:
                    token_value = data[field]
                    if token_value and isinstance(token_value, str):
                        token = token_value.strip()
                        if token.startswith("eyJ"):
                            self.jwt_token = token
                            print(f"✅ JWT found in data.{field}")
                            return True
        
        # Method 3: Nested in user object
        if "user" in response_data and isinstance(response_data["user"], dict):
            user = response_data["user"]
            for field in token_fields:
                if field in user and user[field]:
                    token_value = user[field]
                    if token_value and isinstance(token_value, str):
                        token = token_value.strip()
                        if token.startswith("eyJ"):
                            self.jwt_token = token
                            print(f"✅ JWT found in user.{field}")
                            return True
        
        # Method 4: Authorization header in response
        auth_headers = ["Authorization", "authorization", "Auth", "auth"]
        for header_name in auth_headers:
            auth_header = response_obj.headers.get(header_name)
            if auth_header and isinstance(auth_header, str):
                # Remove "Bearer " prefix if present
                token = auth_header.replace("Bearer ", "").replace("bearer ", "").strip()
                if token and token.startswith("eyJ"):
                    self.jwt_token = token
                    print(f"✅ JWT found in {header_name} header")
                    return True
        
        # Method 5: Cookies
        for cookie in self.session.cookies:
            if any(keyword in cookie.name.lower() for keyword in ["token", "jwt", "auth"]):
                if cookie.value and isinstance(cookie.value, str) and cookie.value.startswith("eyJ"):
                    self.jwt_token = cookie.value
                    print(f"✅ JWT found in cookie: {cookie.name}")
                    return True
        
        # Method 6: Pattern matching for JWT in entire response
        response_text = json.dumps(response_data)
        jwt_pattern = r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
        jwt_matches = re.findall(jwt_pattern, response_text)
        
        if jwt_matches:
            # Take the longest match (likely the complete token)
            self.jwt_token = max(jwt_matches, key=len)
            print("✅ JWT found using pattern matching")
            return True
        
        print("❌ JWT token not found in response")
        print(f"📄 Available response keys: {list(response_data.keys())}")
        
        # Debug: Print partial response (first 500 chars)
        print(f"📄 Response preview: {str(response_data)[:500]}...")
        
        return False
    
    def validate_jwt_token(self) -> bool:
        """Validate and decode JWT token to check expiry"""
        if not self.jwt_token:
            return False
        
        try:
            # Decode JWT to check expiry
            parts = self.jwt_token.split('.')
            if len(parts) != 3:
                print("⚠️  Invalid JWT format")
                return False
            
            # Decode payload
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)
            
            # Check expiry
            if 'exp' in payload_data:
                exp_timestamp = payload_data['exp']
                expiry_time = datetime.fromtimestamp(exp_timestamp)
                current_time = datetime.now()
                
                print(f"🕐 Token expires at: {expiry_time}")
                print(f"⏰ Current time: {current_time}")
                
                if expiry_time > current_time:
                    time_left = expiry_time - current_time
                    print(f"✅ Token valid for: {time_left}")
                    return True
                else:
                    print("❌ Token has expired")
                    return False
            else:
                print("⚠️  No expiry found in token")
                return True
                
        except Exception as e:
            print(f"⚠️  Token validation error: {e}")
            return True  # Assume valid if we can't decode
    
    def fetch_all_invoices(self) -> List[Dict[str, Any]]:
        """Fetch all invoices using the JWT token"""
        print("=" * 60)
        print("📄 FETCHING INVOICES")
        print("=" * 60)
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return []
        
        url = f"{self.base_url}/api/v1/payment/invoice/filter"
        limit = 100
        offset = 0
        all_invoices = []

        # Date range: April 1, 2024 to March 31, 2025
        start_date = "2024-04-01T00:00:00.000Z"
        end_date = "2025-03-31T23:59:59.999Z"

        headers = self.base_headers.copy()
        headers['authorization'] = self.jwt_token

        while True:
            payload = {
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
            }

            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, dict):
                        invoice_list = data.get('data', {}).get('invoiceList', [])
                        all_invoices.extend(invoice_list)
                        has_next = data.get('data', {}).get('hasNext', False)
                        
                        if has_next and len(invoice_list) > 0:
                            offset += limit
                            print(f"📄 Fetched {len(invoice_list)} invoices, total so far: {len(all_invoices)}")
                        else:
                            print(f"✅ Finished fetching invoices. Total: {len(all_invoices)}")
                            break
                elif response.status_code == 401:
                    print("❌ Token expired or invalid for invoices")
                    break
                else:
                    print(f"❌ Failed to fetch invoices: {response.status_code} - {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Invoice fetch error: {e}")
                break

        return all_invoices

    def fetch_all_settlements(self) -> List[Dict[str, Any]]:
        """Fetch all settlements (DN/CN)"""
        print("=" * 60)
        print("🔄 FETCHING SETTLEMENTS (DN/CN)")
        print("=" * 60)
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return []
        
        url = f"{self.base_url}/api/v1/payment/settlement/filter"
        limit = 100
        offset = 0
        all_settlements = []

        start_date = "2024-04-01T18:30:00.000Z"
        end_date = "2025-03-31T18:29:59.999Z"

        headers = {
            'accept': 'application/json',
            'authorization': self.jwt_token,
            'content-type': 'application/json',
        }

        while True:
            payload = {
                "startDate": start_date,
                "endDate": end_date,
                "offset": offset,
                "limit": limit,
                "refNos": [],
                "settlementSubTypes": []
            }

            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, dict):
                        settlement_list = data.get('data', {}).get('settlements', [])
                        all_settlements.extend(settlement_list)
                        has_next = data.get('data', {}).get('hasNext', False)
                        
                        if has_next and len(settlement_list) > 0:
                            offset += limit
                            print(f"🔄 Fetched {len(settlement_list)} settlements, total so far: {len(all_settlements)}")
                        else:
                            print(f"✅ Finished fetching settlements. Total: {len(all_settlements)}")
                            break
                elif response.status_code == 401:
                    print("❌ Token expired or invalid for settlements")
                    break
                else:
                    print(f"❌ Failed to fetch settlements: {response.status_code} - {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Settlement fetch error: {e}")
                break

        return all_settlements

    def fetch_all_payment_advice(self) -> List[Dict[str, Any]]:
        """Fetch all payment advice"""
        print("=" * 60)
        print("💰 FETCHING PAYMENT ADVICE")
        print("=" * 60)
        
        if not self.jwt_token:
            print("❌ No JWT token available")
            return []
        
        url = f"{self.base_url}/api/v1/payment/payment-advice/filter"
        limit = 100
        offset = 0
        all_advices = []

        start_date = "2024-04-01T18:30:00.000Z"
        end_date = "2025-03-31T18:29:59.999Z"

        headers = {
            'accept': 'application/json',
            'authorization': self.jwt_token,
            'content-type': 'application/json',
        }

        while True:
            payload = {
                "startDate": start_date,
                "endDate": end_date,
                "offset": offset,
                "limit": limit,
                "refNos": [],
                "utrNos": []
            }

            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, dict):
                        advice_list = data.get('data', {}).get('paymentAdviceList', [])
                        all_advices.extend(advice_list)
                        has_next = data.get('data', {}).get('hasNext', False)
                        
                        if has_next and len(advice_list) > 0:
                            offset += limit
                            print(f"💰 Fetched {len(advice_list)} payment advices, total so far: {len(all_advices)}")
                        else:
                            print(f"✅ Finished fetching payment advice. Total: {len(all_advices)}")
                            break
                elif response.status_code == 401:
                    print("❌ Token expired or invalid for payment advice")
                    break
                else:
                    print(f"❌ Failed to fetch payment advices: {response.status_code} - {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Payment advice fetch error: {e}")
                break

        return all_advices

    def save_all_data_to_excel(self, invoices: List[Dict[str, Any]], settlements: List[Dict[str, Any]], payment_advice: List[Dict[str, Any]]) -> Optional[str]:
        """Save all data to Excel with multiple sheets"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.vendor_name}_{timestamp}_complete_data.xlsx"
        current_dir = os.getcwd()
        full_path = os.path.join(current_dir, filename)
        
        try:
            print("=" * 60)
            print("💾 SAVING DATA TO EXCEL")
            print("=" * 60)
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Save invoices
                if invoices:
                    df_invoices = pd.DataFrame(invoices)
                    df_invoices.to_excel(writer, sheet_name='Invoices', index=False)
                    print(f"✅ Saved {len(invoices)} invoices to 'Invoices' sheet")
                else:
                    pd.DataFrame({'Message': ['No invoice data found for the date range']}).to_excel(
                        writer, sheet_name='Invoices', index=False)
                    print("⚠️  No invoices found - created empty 'Invoices' sheet")

                # Save settlements
                if settlements:
                    df_settlements = pd.DataFrame(settlements)
                    df_settlements.to_excel(writer, sheet_name='DN_CN', index=False)
                    print(f"✅ Saved {len(settlements)} settlements to 'DN_CN' sheet")
                else:
                    pd.DataFrame({'Message': ['No settlement data found for the date range']}).to_excel(
                        writer, sheet_name='DN_CN', index=False)
                    print("⚠️  No settlements found - created empty 'DN_CN' sheet")

                # Save payment advice
                if payment_advice:
                    df_payment_advice = pd.DataFrame(payment_advice)
                    df_payment_advice.to_excel(writer, sheet_name='Payment_Advice', index=False)
                    print(f"✅ Saved {len(payment_advice)} payment advices to 'Payment_Advice' sheet")
                else:
                    pd.DataFrame({'Message': ['No payment advice data found for the date range']}).to_excel(
                        writer, sheet_name='Payment_Advice', index=False)
                    print("⚠️  No payment advice found - created empty 'Payment_Advice' sheet")

            print("=" * 60)
            print("🎉 SUCCESS! All data saved to Excel")
            print("=" * 60)
            print(f"📁 File: {filename}")
            print(f"🗂️  Full Path: {full_path}")
            print("📊 Sheets created:")
            print("   1. Invoices - All invoice data")
            print("   2. DN_CN - All settlement data (Debit/Credit Notes)")
            print("   3. Payment_Advice - All payment advice data")
            print(f"📅 Date Range: April 1, 2024 to March 31, 2025")
            print("=" * 60)
            
            return filename

        except Exception as e:
            print(f"❌ Failed to save Excel file: {e}")
            return None

    def test_jwt_token_manually(self, manual_token: str) -> bool:
        """Test a manually provided JWT token"""
        print("🧪 Testing manually provided JWT token...")
        
        self.jwt_token = manual_token.strip()
        
        if not self.validate_jwt_token():
            return False
        
        # Test token with a simple API call
        try:
            headers = {
                'accept': 'application/json',
                'authorization': self.jwt_token,
                'content-type': 'application/json',
            }
            
            test_payload = {
                "startDate": "2024-04-01T00:00:00.000Z",
                "endDate": "2024-04-02T00:00:00.000Z",
                "offset": 0,
                "limit": 1,
                "statusList": [],
                "refNos": [],
                "poNos": [],
                "asnNos": [],
                "invoiceNos": [],
                "vendorCodes": []
            }
            
            test_response = requests.post(
                f"{self.base_url}/api/v1/payment/invoice/filter",
                headers=headers,
                data=json.dumps(test_payload),
                timeout=30
            )
            
            if test_response.status_code == 200:
                print("✅ JWT token is valid and working!")
                return True
            elif test_response.status_code == 401:
                print("❌ JWT token is invalid or expired")
                return False
            else:
                print(f"⚠️  Unexpected response: {test_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Token test error: {e}")
            return False

    def run_complete_automation(self, email: str, password: str, n8n_webhook_url: str) -> bool:
        """Main method: Complete automation from login to data download"""
        print("🚀 ZEPTO COMPLETE AUTOMATION STARTED")
        print("=" * 60)
        print(f"📧 Email: {email}")
        print(f"🏢 Vendor: {self.vendor_name}")
        print(f"🕐 Started at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"👤 User: RG2445-Nakad")
        print("=" * 60)
        
        # Step 1: Complete login flow
        login_success = self.complete_login_flow(email, password, n8n_webhook_url)
        
        if not login_success:
            print("❌ Automated login flow failed.")
            print("🔧 Fallback: Manual JWT token input")
            
            try:
                manual_token = input("\nPlease paste your JWT token here: ").strip()
                if manual_token and self.test_jwt_token_manually(manual_token):
                    print("✅ Manual token accepted! Proceeding with data extraction...")
                else:
                    print("❌ Manual token is invalid. Exiting...")
                    return False
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled by user")
                return False
            except:
                print("❌ Failed to get manual token. Exiting...")
                return False
        
        print("✅ Authentication successful! Proceeding with data extraction...")
        print("=" * 60)
        
        # Step 2: Fetch all data
        print("📊 Starting data extraction...")
        
        invoices = self.fetch_all_invoices()
        settlements = self.fetch_all_settlements()
        payment_advice = self.fetch_all_payment_advice()
        
        # Step 3: Save to Excel
        filename = self.save_all_data_to_excel(invoices, settlements, payment_advice)
        
        # Final summary
        if filename:
            print("🎯 AUTOMATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("📈 FINAL SUMMARY:")
            print(f"   📄 Invoices: {len(invoices)} records")
            print(f"   🔄 Settlements (DN/CN): {len(settlements)} records")
            print(f"   💰 Payment Advice: {len(payment_advice)} records")
            print(f"   📁 File: {filename}")
            print(f"   📂 Location: {os.getcwd()}")
            print(f"   ⏰ Completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print("=" * 60)
            print("🎉 All done! Check your current directory for the Excel file.")
            return True
        else:
            print("❌ Failed to save data. Automation incomplete.")
            return False

    def run_with_manual_token(self, jwt_token: str) -> bool:
        """Run data extraction with manually provided JWT token"""
        print("🔧 RUNNING WITH MANUAL JWT TOKEN")
        print("=" * 60)
        print(f"🏢 Vendor: {self.vendor_name}")
        print(f"🕐 Started at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"👤 User: RG2445-Nakad")
        print("=" * 60)
        
        # Test the provided token
        if not self.test_jwt_token_manually(jwt_token):
            print("❌ Provided JWT token is invalid or expired")
            return False
        
        print("✅ JWT token validated! Proceeding with data extraction...")
        print("=" * 60)
        
        # Fetch all data
        print("📊 Starting data extraction...")
        
        invoices = self.fetch_all_invoices()
        settlements = self.fetch_all_settlements()
        payment_advice = self.fetch_all_payment_advice()
        
        # Save to Excel
        filename = self.save_all_data_to_excel(invoices, settlements, payment_advice)
        
        # Final summary
        if filename:
            print("🎯 MANUAL TOKEN EXTRACTION COMPLETED!")
            print("=" * 60)
            print("📈 FINAL SUMMARY:")
            print(f"   📄 Invoices: {len(invoices)} records")
            print(f"   🔄 Settlements (DN/CN): {len(settlements)} records")
            print(f"   💰 Payment Advice: {len(payment_advice)} records")
            print(f"   📁 File: {filename}")
            print(f"   📂 Location: {os.getcwd()}")
            print(f"   ⏰ Completed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print("=" * 60)
            return True
        else:
            print("❌ Failed to save data.")
            return False


def main() -> None:
    """Main execution function - Configured for Sanfe"""
    print("🔧 ZEPTO AUTOMATION FOR SANFE")
    print("=" * 60)
    
    # ============================================================================
    # ✅ SANFE CONFIGURATION - READY TO USE
    # ============================================================================
    
    EMAIL = "operations@sanfe.in"
    PASSWORD = "Sanfezepto@9818"
    N8N_WEBHOOK_URL = "https://nakad-arp.app.n8n.cloud/workflow/ncVakShiGjTIQ40p"
    VENDOR_NAME = "Sanfe"
    
    # Optional: Use manual JWT token instead of automated login
    MANUAL_JWT_TOKEN = ""  # Leave empty for automated login
    
    # ============================================================================
    
    print(f"📧 Email: {EMAIL}")
    print(f"🏢 Vendor: {VENDOR_NAME}")
    print(f"🔗 n8n Webhook: {N8N_WEBHOOK_URL}")
    print(f"🔑 Manual Token: {'Yes' if MANUAL_JWT_TOKEN else 'No (Automated Login)'}")
    print(f"👤 User: RG2445-Nakad")
    print(f"📅 Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 60)
    
    # Create automation instance
    automation = CompleteZeptoAutomation(VENDOR_NAME)
    
    # Choose execution method
    if MANUAL_JWT_TOKEN:
        print("🔧 Using manual JWT token mode...")
        success = automation.run_with_manual_token(MANUAL_JWT_TOKEN)
    else:
        print("🤖 Using automated login mode...")
        success = automation.run_complete_automation(EMAIL, PASSWORD, N8N_WEBHOOK_URL)
    
    # Final result
    if success:
        print("✅ All done! Check your current directory for the Excel file.")
        print("📂 File saved in:", os.getcwd())
    else:
        print("❌ Automation failed. Please check the logs above.")


if __name__ == "__main__":
    main()