#import os.path
#import base64
#from email import message_from_bytes

#from google.oauth2.credentials import Credentials
#from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import Request
#from googleapiclient.discovery import build

#SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

#def get_gmail_service():
    #creds = None

    #if os.path.exists('token.json'):
        #creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    #if not creds or not creds.valid:
        #if creds and creds.expired and creds.refresh_token:
            #creds.refresh(Request())
        #else:
            #flow = InstalledAppFlow.from_client_secrets_file(
                #'credentials.json', SCOPES)
            #creds = flow.run_local_server(port=0)

        #with open('token.json', 'w') as token:
            #token.write(creds.to_json())

    #service = build('gmail', 'v1', credentials=creds)
    #return service


#def fetch_unread_rfq_replies():
    #service = get_gmail_service()

    # Search unread mails containing RFQ
    #results = service.users().messages().list(
        #userId='me',
        #q='is:unread subject:RFQ'
    #).execute()

    #messages = results.get('messages', [])

    #emails = []

    #if not messages:
        #return emails

    #for msg in messages:
        #msg_data = service.users().messages().get(
            #userId='me',
            #id=msg['id'],
            #format='raw'
        #).execute()

        #raw_data = base64.urlsafe_b64decode(msg_data['raw'])
        #email_message = message_from_bytes(raw_data)

        #subject = email_message['Subject']
        #from_email = email_message['From']

        #body = ""

        #if email_message.is_multipart():
            #for part in email_message.walk():
                #if part.get_content_type() == "text/plain":
                    #body = part.get_payload(decode=True).decode()
        #else:
            #body = email_message.get_payload(decode=True).decode()

        #emails.append({
            #"id": msg['id'],
            #"subject": subject,
            #"from": from_email,
            #"body": body
        #})

        # Mark as read
        #service.users().messages().modify(
            #userId='me',
            #id=msg['id'],
            #body={'removeLabelIds': ['UNREAD']}
        #).execute()

    #return emails

# import base64
# import re
# import sqlite3
# import requests
# import json

# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

# import os
# import pickle

# SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# # ==============================
# # GMAIL CONNECTION
# # ==============================

# def get_gmail_service():

#     creds = None

#     if os.path.exists("token.pickle"):
#         with open("token.pickle", "rb") as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:

#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())

#         else:

#             flow = InstalledAppFlow.from_client_secrets_file(
#                 "credentials.json",
#                 SCOPES
#             )

#             creds = flow.run_local_server(port=0)

#         with open("token.pickle", "wb") as token:
#             pickle.dump(creds, token)

#     return build("gmail", "v1", credentials=creds)

# token_match = re.search(r'RFQ TOKEN:\s*([a-zA-Z0-9\-]+)', body)

# if not token_match:
#     print("RFQ token not found")
#     continue

# rfq_token = token_match.group(1)
# # ==============================
# # AI QUOTE EXTRACTION (OLLAMA)
# # ==============================

# def extract_vendor_quote(body):

#     prompt = f"""
# Extract vendor quotation details from the email.

# Return JSON format only.

# Fields:
# unit_price
# delivery_days
# payment_terms

# Email:
# {body}
# """

#     try:

#         response = requests.post(
#             "http://localhost:11434/api/generate",
#             json={
#                 "model": "llama3",
#                 "prompt": prompt,
#                 "stream": False
#             }
#         )

#         result = response.json()["response"]

#         data = json.loads(result)

#         return data

#     except:

#         return {}


# # ==============================
# # STORE VENDOR QUOTE
# # ==============================

# def save_quote(rfq_id, sender_email, body):

#     conn = sqlite3.connect("procurement.db")
#     cursor = conn.cursor()

#     # Check if already processed
#     cursor.execute("""
#     SELECT status FROM rfq_vendors
#     WHERE rfq_id=? AND vendor_email=?
#     """, (rfq_id, sender_email))

#     row = cursor.fetchone()

#     if not row:
#         print("Vendor not found in RFQ list")
#         conn.close()
#         return

#     if row[0] == "Quote Received":
#         print("Quote already processed")
#         conn.close()
#         return

#     # AI Extraction
#     ai_data = extract_vendor_quote(body)

#     unit_price = ai_data.get("unit_price")
#     delivery_days = ai_data.get("delivery_days")
#     payment_terms = ai_data.get("payment_terms")

#     print("AI Extracted Data:", ai_data)

#     # Update database
#     cursor.execute("""
#     UPDATE rfq_vendors
#     SET status='Quote Received'
#     WHERE rfq_id=? AND vendor_email=?
#     """, (rfq_id, sender_email))

#     cursor.execute("""
#     INSERT INTO vendor_quotes
#     (material_id, vendor_id, unit_price, delivery_days, payment_terms)
#     VALUES (?, ?, ?, ?, ?)
#     """, (rfq_id, 1, unit_price, delivery_days, payment_terms))

#     conn.commit()
#     conn.close()

#     print("Vendor quote saved")


# # ==============================
# # FETCH RFQ REPLIES
# # ==============================

# def fetch_rfq_replies():

#     conn = sqlite3.connect("procurement.db")
#     cursor = conn.cursor()

#     cursor.execute("""
#     SELECT id FROM rfq_vendors
#     WHERE rfq_id=? AND vendor_email=?
#     """, (rfq_id, sender_email))

#     vendor = cursor.fetchone()

#     if not vendor:
#         print("Email not from RFQ vendor — skipping")
#         continue

#     print("Checking mailbox for RFQ replies...")

#     service = get_gmail_service()

#     # results = service.users().messages().list(
#     #     userId='me',
#     #     labelIds=['INBOX'],
#     #     maxResults=20
#     # ).execute()
#     results = service.users().messages().list(
#         userId='me',
#         labelIds=['INBOX'],
#         q="subject:RFQ- newer_than:7d"
#     ).execute()

#     messages = results.get('messages', [])

#     print("Messages found:", len(messages))

#     for message in messages:

#         msg = service.users().messages().get(
#             userId='me',
#             id=message['id']
#         ).execute()

#         payload = msg['payload']
#         headers = payload.get("headers")

#         subject = ""
#         sender = ""

#         for header in headers:

#             if header['name'] == 'Subject':
#                 subject = header['value']

#             if header['name'] == 'From':
#                 sender = header['value']

#         # STRICT RFQ SUBJECT CHECK
#         match = re.match(r'RFQ-(\d+)\s*\|\s*PRJ-\d+\s*\|', subject)

#         if not match:
#             continue

#         rfq_id = int(match.group(1))

#         # Extract email
#         sender_email = re.findall(r'<(.+?)>', sender)

#         if sender_email:
#             sender_email = sender_email[0]
#         else:
#             sender_email = sender

#         # GET EMAIL BODY
#         body = ""

#         if 'parts' in payload:

#             for part in payload['parts']:

#                 if part['mimeType'] == 'text/plain':

#                     data = part['body'].get('data')

#                     if data:
#                         decoded = base64.urlsafe_b64decode(data)
#                         body = decoded.decode()

#         else:

#             data = payload['body'].get('data')

#             if data:
#                 decoded = base64.urlsafe_b64decode(data)
#                 body = decoded.decode()

#         print("\nVendor Reply Found")
#         print("RFQ:", rfq_id)
#         print("Vendor:", sender_email)
#         print("EMAIL BODY:")
#         print(body)

#         save_quote(rfq_id, sender_email, body)

#     print("\nFinished checking emails.")

# import base64
# import re
# import sqlite3
# import os
# import pickle

# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# import sqlite3

# from services.db import get_connection
# conn = get_connection()
# cursor = conn.cursor()

# from services.ai_extractor import extract_vendor_quote


# SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# # =====================================
# # GMAIL CONNECTION
# # =====================================

# def get_gmail_service():

#     creds = None

#     if os.path.exists("token.pickle"):
#         with open("token.pickle", "rb") as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:

#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())

#         else:

#             flow = InstalledAppFlow.from_client_secrets_file(
#                 "credentials.json",
#                 SCOPES
#             )

#             creds = flow.run_local_server(port=0)

#         with open("token.pickle", "wb") as token:
#             pickle.dump(creds, token)

#     return build("gmail", "v1", credentials=creds)


# # =====================================
# # SAVE VENDOR QUOTE
# # =====================================

# def save_quote(rfq_id, sender_email, body):

#     # conn = sqlite3.connect("procurement.db")
#     # cursor = conn.cursor()

#     cursor.execute("""
#     SELECT status FROM rfq_vendors
#     WHERE rfq_id=? AND vendor_email=?
#     """, (rfq_id, sender_email))

#     row = cursor.fetchone()

#     if not row:
#         print("Vendor not found in RFQ list")
#         conn.close()
#         return

#     if row[0] == "Quote Received":
#         print("Quote already processed")
#         conn.close()
#         return
    
#     print("EMAIL BODY:")
#     print(body)
#     print("---------------------")

#     # ======================
#     # AI EXTRACTION
#     # ======================

#     ai_data = extract_vendor_quote(body)

#     unit_price = ai_data.get("unit_price")
#     delivery_days = ai_data.get("delivery_time")
#     payment_terms = ai_data.get("payment_terms")

#     print("AI Extracted:", ai_data)
#     ai_data = extract_vendor_quote(body)

#     unit_price = ai_data.get("unit_price")
#     delivery_days = ai_data.get("delivery_days")
#     payment_terms = ai_data.get("payment_terms")

# #     import re

# # # Unit price fallback
# #     if not unit_price:
# #         match = re.search(r'(\d+)\s*(INR|Rs|USD)?', body, re.IGNORECASE)
# #         if match:
# #             unit_price = match.group(1)

# # # Delivery fallback
# #     if not delivery_days:
# #         match = re.search(r'delivery[:\- ]*(.+)', body, re.IGNORECASE)
# #         if match:
# #             delivery_days = match.group(1).strip()

# # # Payment fallback
# #     if not payment_terms:
# #         match = re.search(r'payment[:\- ]*(.+)', body, re.IGNORECASE)
# #         if match:
# #             payment_terms = match.group(1).strip()
# #     print("Extracted:", unit_price, delivery_days, payment_terms)
#     # import re

#     # price_match = re.search(r"unit\s*price\s*[:\-]?\s*(\d+)", body, re.I)
#     # delivery_match = re.search(r"delivery\s*[:\-]?\s*(.*)", body, re.I)
#     # payment_match = re.search(r"payment\s*terms\s*[:\-]?\s*(.*)", body, re.I)

#     # unit_price = price_match.group(1) if price_match else None
#     # delivery = delivery_match.group(1) if delivery_match else None
#     # payment = payment_match.group(1) if payment_match else None

#     # cursor.execute("""
#     # UPDATE rfq_vendors
#     # SET status='Quote Received'
#     # WHERE rfq_id=? AND vendor_email=?
#     # """, (rfq_id, sender_email))

#     # cursor.execute("""
#     # INSERT INTO vendor_quotes
#     # (material_id, vendor_id, unit_price, delivery_days, payment_terms)
#     # VALUES (?, ?, ?, ?, ?)
#     # """, (rfq_id, 1, unit_price, delivery_days, payment_terms))

#     # cursor.execute("""
#     # UPDATE rfq_vendors
#     # SET
#     #     unit_price = ?,
#     #     delivery_time = ?,
#     #     payment_terms = ?,
#     #     raw_email = ?,
#     #     received_date = datetime('now'),
#     #     status = 'Quote Received'
#     # WHERE rfq_id = ? AND vendor_email = ?
#     # """, (unit_price, delivery_days, payment_terms, body, rfq_id, sender_email))
#     # cursor.execute("""
#     # UPDATE rfq_vendors
#     # SET unit_price=?, delivery_time=?, payment_terms=?
#     # WHERE rfq_id=? AND vendor_name=?
#     # """, (
#     #     row["Unit Price"],
#     #     row["Delivery Time"],
#     #     row["Payment Terms"],
#     #     row["RFQ ID"],
#     #     row["Vendor"]
#     # ))

#     # conn.commit()
#     # conn.close()
#     import re

#     cursor.execute("SELECT id, raw_email FROM rfq_vendors WHERE unit_price IS NULL")
#     rows = cursor.fetchall()

#     for r in rows:
#         email = r["raw_email"]

#         if email:
#             price = re.search(r"unit\s*price.*?(\d+)", email, re.I)
#             delivery = re.search(r"delivery.*?:\s*(.*)", email, re.I)
#             payment = re.search(r"payment.*?:\s*(.*)", email, re.I)

#             unit_price = float(price.group(1)) if price else None
#             delivery_time = delivery.group(1) if delivery else None
#             payment_terms = payment.group(1) if payment else None

#             cursor.execute("""
#             UPDATE rfq_vendors
#             SET unit_price=?, delivery_time=?, payment_terms=?
#             WHERE id=?
#             """, (unit_price, delivery_time, payment_terms, r["id"]))

#     conn.commit()

#     print("Quote stored successfully")


# # =====================================
# # EMAIL BODY EXTRACTOR
# # =====================================

# def get_email_body(payload):

#     body = ""

#     if 'parts' in payload:

#         for part in payload['parts']:

#             mime = part.get("mimeType")

#             if mime == "text/plain":

#                 data = part['body'].get('data')

#                 if data:
#                     decoded = base64.urlsafe_b64decode(data)
#                     body = decoded.decode(errors="ignore")
#                     return body

#             if 'parts' in part:

#                 for subpart in part['parts']:

#                     if subpart.get("mimeType") == "text/plain":

#                         data = subpart['body'].get('data')

#                         if data:
#                             decoded = base64.urlsafe_b64decode(data)
#                             body = decoded.decode(errors="ignore")
#                             return body

#     else:

#         data = payload['body'].get('data')

#         if data:
#             decoded = base64.urlsafe_b64decode(data)
#             body = decoded.decode(errors="ignore")

#     return body


# # =====================================
# # FETCH RFQ EMAIL REPLIES
# # =====================================

# def fetch_rfq_replies():

#     print("Checking mailbox for RFQ replies...")

#     service = get_gmail_service()

#     results = service.users().messages().list(
#         userId='me',
#         labelIds=['INBOX'],
#         #q="subject:RFQ newer_than:7d"
#         q="subject:RFQ is:unread"
#     ).execute()

#     messages = results.get('messages', [])

#     print("Messages found:", len(messages))

#     for message in messages:

#         msg = service.users().messages().get(
#             userId='me',
#             id=message['id']
#         ).execute()

#         payload = msg['payload']
#         headers = payload.get("headers")

#         subject = ""
#         sender = ""

#         for header in headers:

#             if header['name'] == 'Subject':
#                 subject = header['value']

#             if header['name'] == 'From':
#                 sender = header['value']

#         # ======================
#         # RFQ ID EXTRACT
#         # ======================

#         rfq_match = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)

#         if not rfq_match:
#             continue

#         rfq_id = int(rfq_match.group(1))

#         # ======================
#         # EMAIL EXTRACT
#         # ======================

#         sender_email = re.findall(r'<(.+?)>', sender)

#         if sender_email:
#             sender_email = sender_email[0]
#         else:
#             sender_email = sender

#         body = get_email_body(payload)

#         print("\nVendor Reply Found")
#         print("RFQ:", rfq_id)
#         print("Vendor:", sender_email)

#         save_quote(rfq_id, sender_email, body)

#     print("Mailbox scan complete")

# import base64
# import re
# import os
# import pickle

# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

# from services.db import get_connection
# from services.ai_extractor import extract_vendor_quote

# SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# # =====================================
# # GMAIL CONNECTION
# # =====================================

# def get_gmail_service():

#     creds = None

#     if os.path.exists("token.pickle"):
#         with open("token.pickle", "rb") as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:

#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())

#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 "credentials.json",
#                 SCOPES
#             )
#             creds = flow.run_local_server(port=0)

#         with open("token.pickle", "wb") as token:
#             pickle.dump(creds, token)

#     service = build("gmail", "v1", credentials=creds)

#     return service


# # =====================================
# # SAVE VENDOR QUOTE
# # =====================================

# def save_quote(rfq_id, sender_email, body):

#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT status FROM vendor_quotes
#         WHERE rfq_id=? AND vendor_email=?
#     """, (rfq_id, sender_email))

#     row = cursor.fetchone()

#     if not row:
#         print("Vendor not found in RFQ list")
#         conn.close()
#         return

#     if row["status"] == "Quote Received":
#         print("Quote already processed")
#         conn.close()
#         return

#     print("EMAIL BODY:")
#     print(body)
#     print("----------------------")

#     # ======================
#     # AI EXTRACTION
#     # ======================

#     ai_data = extract_vendor_quote(body)

#     unit_price = ai_data.get("unit_price")
#     delivery_days = ai_data.get("delivery_days")
#     payment_terms = ai_data.get("payment_terms")

#     print("AI Extracted:", ai_data)

#     # ======================
#     # FALLBACK REGEX (if AI fails)
#     # ======================

#     if not unit_price:
#         price_match = re.search(r'(\d{3,6})', body)
#         if price_match:
#             unit_price = float(price_match.group(1))

#     if not delivery_days:
#         delivery_match = re.search(r'(\d+\s*(days|weeks))', body, re.IGNORECASE)
#         if delivery_match:
#             delivery_days = delivery_match.group(1)

#     if not payment_terms:
#         payment_match = re.search(r'(\d+\s*days\s*credit)', body, re.IGNORECASE)
#         if payment_match:
#             payment_terms = payment_match.group(1)

#     print("Final Extracted:",
#           unit_price,
#           delivery_days,
#           payment_terms)

#     # ======================
#     # SAVE TO DATABASE
#     # ======================

#     cursor.execute("""
#         UPDATE vendor_quotes
#         SET
#             unit_price = ?,
#             delivery_time = ?,
#             payment_terms = ?,
#             raw_email = ?,
#             email_received_date = datetime('now'),
#             status = 'Quote Received'
#         WHERE rfq_id = ? AND vendor_email = ?
#     """, (
#         unit_price,
#         delivery_days,
#         payment_terms,
#         body,
#         rfq_id,
#         sender_email
#     ))

#     conn.commit()
#     conn.close()

#     print("Quote stored successfully")


# # =====================================
# # EMAIL BODY EXTRACTOR
# # =====================================

# def get_email_body(payload):

#     body = ""

#     if 'parts' in payload:

#         for part in payload['parts']:

#             mime = part.get("mimeType")

#             if mime == "text/plain":

#                 data = part['body'].get('data')

#                 if data:
#                     decoded = base64.urlsafe_b64decode(data)
#                     body = decoded.decode(errors="ignore")
#                     return body

#             if 'parts' in part:

#                 for subpart in part['parts']:

#                     if subpart.get("mimeType") == "text/plain":

#                         data = subpart['body'].get('data')

#                         if data:
#                             decoded = base64.urlsafe_b64decode(data)
#                             body = decoded.decode(errors="ignore")
#                             return body

#     else:

#         data = payload['body'].get('data')

#         if data:
#             decoded = base64.urlsafe_b64decode(data)
#             body = decoded.decode(errors="ignore")

#     return body


# # =====================================
# # FETCH RFQ EMAIL REPLIES
# # =====================================

# def fetch_rfq_replies():

#     print("Checking mailbox for RFQ replies...")

#     service = get_gmail_service()

#     results = service.users().messages().list(
#         userId='me',
#         labelIds=['INBOX'],
#         q="subject:RFQ is:unread"
#     ).execute()

#     messages = results.get('messages', [])

#     print("Messages found:", len(messages))

#     for message in messages:

#         msg = service.users().messages().get(
#             userId='me',
#             id=message['id']
#         ).execute()

#         payload = msg['payload']
#         headers = payload.get("headers")

#         subject = ""
#         sender = ""

#         for header in headers:

#             if header['name'] == 'Subject':
#                 subject = header['value']

#             if header['name'] == 'From':
#                 sender = header['value']

#         # ======================
#         # RFQ ID EXTRACT
#         # ======================

#         rfq_match = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)

#         if not rfq_match:
#             continue

#         rfq_id = int(rfq_match.group(1))

#         # ======================
#         # EXTRACT SENDER EMAIL
#         # ======================

#         sender_email = re.findall(r'<(.+?)>', sender)

#         if sender_email:
#             sender_email = sender_email[0]
#         else:
#             sender_email = sender

#         # ======================
#         # EMAIL BODY
#         # ======================

#         body = get_email_body(payload)

#         print("\nVendor Reply Found")
#         print("RFQ:", rfq_id)
#         print("Vendor:", sender_email)

#         save_quote(rfq_id, sender_email, body)

#     print("Mailbox scan complete")

# import base64
# import re
# import os
# import pickle

# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

# from services.db import get_connection
# from services.ai_extractor import extract_vendor_quote
# from services.pdf_reader import extract_pdf_text


# SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# # =====================================
# # GMAIL CONNECTION
# # =====================================

# def get_gmail_service():

#     creds = None

#     if os.path.exists("token.pickle"):
#         with open("token.pickle", "rb") as token:
#             creds = pickle.load(token)

#     if not creds or not creds.valid:

#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())

#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 "credentials.json",
#                 SCOPES
#             )
#             creds = flow.run_local_server(port=0)

#         with open("token.pickle", "wb") as token:
#             pickle.dump(creds, token)

#     service = build("gmail", "v1", credentials=creds)

#     return service


# # =====================================
# # SAVE VENDOR QUOTE
# # =====================================

# def save_quote(rfq_id, sender_email, body):

#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT status FROM vendor_quotes
#         WHERE rfq_id=? AND vendor_email=?
#     """, (rfq_id, sender_email))

#     row = cursor.fetchone()

#     if not row:
#         print("Vendor not found in RFQ list")
#         conn.close()
#         return

#     if row["status"] == "Quote Received":
#         print("Quote already processed")
#         conn.close()
#         return

#     print("EMAIL BODY:")
#     print(body)
#     print("----------------------")

#     # ======================
#     # AI EXTRACTION
#     # ======================

#     ai_data = extract_vendor_quote(body)

#     unit_price = ai_data.get("unit_price")
#     delivery_days = ai_data.get("delivery_days")
#     payment_terms = ai_data.get("payment_terms")

#     print("AI Extracted:", ai_data)

#     # ======================
#     # FALLBACK REGEX (if AI fails)
#     # ======================

#     if not unit_price:
#         price_match = re.search(r'(\d{3,6})', body)
#         if price_match:
#             unit_price = float(price_match.group(1))

#     if not delivery_days:
#         delivery_match = re.search(r'(\d+\s*(days|weeks))', body, re.IGNORECASE)
#         if delivery_match:
#             delivery_days = delivery_match.group(1)

#     if not payment_terms:
#         payment_match = re.search(r'(\d+\s*days\s*credit)', body, re.IGNORECASE)
#         if payment_match:
#             payment_terms = payment_match.group(1)

#     print("Final Extracted:",
#           unit_price,
#           delivery_days,
#           payment_terms)

#     # ======================
#     # SAVE TO DATABASE
#     # ======================

#     cursor.execute("""
#         UPDATE vendor_quotes
#         SET
#             unit_price = ?,
#             delivery_time = ?,
#             payment_terms = ?,
#             raw_email = ?,
#             email_received_date = datetime('now'),
#             status = 'Quote Received'
#         WHERE rfq_id = ? AND vendor_email = ?
#     """, (
#         unit_price,
#         delivery_days,
#         payment_terms,
#         body,
#         rfq_id,
#         sender_email
#     ))

#     conn.commit()
#     conn.close()

#     print("Quote stored successfully")


# # =====================================
# # EMAIL BODY EXTRACTOR
# # =====================================

# def get_email_body(payload):

#     body = ""

#     if 'parts' in payload:

#         for part in payload['parts']:

#             mime = part.get("mimeType")

#             if mime == "text/plain":

#                 data = part['body'].get('data')

#                 if data:
#                     decoded = base64.urlsafe_b64decode(data)
#                     body = decoded.decode(errors="ignore")
#                     return body

#             if 'parts' in part:

#                 for subpart in part['parts']:

#                     if subpart.get("mimeType") == "text/plain":

#                         data = subpart['body'].get('data')

#                         if data:
#                             decoded = base64.urlsafe_b64decode(data)
#                             body = decoded.decode(errors="ignore")
#                             return body

#     else:

#         data = payload['body'].get('data')

#         if data:
#             decoded = base64.urlsafe_b64decode(data)
#             body = decoded.decode(errors="ignore")

#     return body


# # =====================================
# # FETCH RFQ EMAIL REPLIES
# # =====================================

# def fetch_rfq_replies():

#     print("Checking mailbox for RFQ replies...")

#     service = get_gmail_service()

#     results = service.users().messages().list(
#         userId='me',
#         labelIds=['INBOX'],
#         q="subject:RFQ is:unread"
#     ).execute()

#     messages = results.get('messages', [])

#     print("Messages found:", len(messages))

#     for message in messages:

#         msg = service.users().messages().get(
#             userId='me',
#             id=message['id']
#         ).execute()

#         payload = msg['payload']
#         headers = payload.get("headers")

#         subject = ""
#         sender = ""

#         for header in headers:

#             if header['name'] == 'Subject':
#                 subject = header['value']

#             if header['name'] == 'From':
#                 sender = header['value']

#         # ======================
#         # RFQ ID EXTRACT
#         # ======================

#         rfq_match = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)

#         if not rfq_match:
#             continue

#         rfq_id = int(rfq_match.group(1))

#         # ======================
#         # EXTRACT SENDER EMAIL
#         # ======================

#         sender_email = re.findall(r'<(.+?)>', sender)

#         if sender_email:
#             sender_email = sender_email[0]
#         else:
#             sender_email = sender

#         # ======================
#         # EMAIL BODY
#         # ======================

#         body = get_email_body(payload)

#         full_text = body

#         # ======================
#         # PDF ATTACHMENT READER
#         # ======================

#         if 'parts' in payload:

#             for part in payload['parts']:

#                 filename = part.get("filename")

#                 if filename and filename.lower().endswith(".pdf"):

#                     attachment_id = part['body'].get('attachmentId')

#                     if attachment_id:

#                         attachment = service.users().messages().attachments().get(
#                             userId='me',
#                             messageId=message['id'],
#                             id=attachment_id
#                         ).execute()

#                         data = attachment['data']
#                         file_data = base64.urlsafe_b64decode(data)

#                         os.makedirs("attachments", exist_ok=True)

#                         filepath = os.path.join("attachments", filename)

#                         with open(filepath, "wb") as f:
#                             f.write(file_data)

#                         pdf_text = extract_pdf_text(filepath)

#                         full_text = full_text + "\n\nPDF CONTENT:\n" + pdf_text

#         print("\nVendor Reply Found")
#         print("RFQ:", rfq_id)
#         print("Vendor:", sender_email)

#         save_quote(rfq_id, sender_email, full_text)

#     print("Mailbox scan complete")
#Correct code
# import re
# import imaplib
# import email
# import streamlit as st

# from services.db import get_connection
# from services.ai_extractor import extract_vendor_quote


# # =====================================
# # GMAIL CONNECTION (IMAP)
# # =====================================

# def get_gmail_connection():

#     EMAIL = st.secrets["EMAIL"]
#     APP_PASSWORD = st.secrets["APP_PASSWORD"]

#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(EMAIL, APP_PASSWORD)

#     return mail


# # =====================================
# # SAVE VENDOR QUOTE
# # =====================================

# def save_quote(rfq_id, sender_email, body):

#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT status FROM vendor_quotes
#         WHERE rfq_id=%s AND vendor_email=%s
#     """, (rfq_id, sender_email))

#     row = cursor.fetchone()

#     if not row:
#         print("Vendor not found in RFQ list")
#         conn.close()
#         return

#     if row["status"] == "Quote Received":
#         print("Quote already processed")
#         conn.close()
#         return

#     print("\nEMAIL BODY:")
#     print(body)
#     print("----------------------")

#     # ======================
#     # AI EXTRACTION
#     # ======================
#     # ai_data = extract_vendor_quote(body)

#     # unit_price = ai_data.get("unit_price")
#     # delivery_days = ai_data.get("delivery_days")
#     # payment_terms = ai_data.get("payment_terms")

#     # print("AI Extracted:", ai_data)

#     # ======================
#     # FALLBACK REGEX
#     # ======================
#     # if not unit_price:
#     #     price_match = re.search(r'(?:Rs\.?|INR)?\s?(\d{3,7})', body, re.IGNORECASE)
#     #     if price_match:
#     #         unit_price = float(price_match.group(1))

#     # if not delivery_days:
#     #     delivery_match = re.search(r'(\d+\s*(days|weeks))', body, re.IGNORECASE)
#     #     if delivery_match:
#     #         delivery_days = delivery_match.group(1)

#     # if not payment_terms:
#     #     payment_match = re.search(r'(advance|credit|payment.*)', body, re.IGNORECASE)
#     #     if payment_match:
#     #         payment_terms = payment_match.group(1)

#     # print("Final Extracted:", unit_price, delivery_days, payment_terms)

#     ai_data = extract_vendor_quote(body)

#     unit_price = ai_data.get("unit_price")
#     delivery_days = ai_data.get("delivery_days")
#     payment_terms = ai_data.get("payment_terms")

#     print("AI Extracted:", ai_data)

# # ======================
# # FALLBACK REGEX
# # ======================

#     if not unit_price:
#         price_match = re.search(r'(?:Rs\.?|INR)?\s?(\d{2,7})', body, re.IGNORECASE)
#         if price_match:
#             unit_price = float(price_match.group(1))

#     if not delivery_days:
#         delivery_match = re.search(r'(\d+\s*(days?|weeks?))', body, re.IGNORECASE)
#         if delivery_match:
#             delivery_days = delivery_match.group(1)

#     if not payment_terms:
#         payment_match = re.search(r'(advance|credit|payment.*)', body, re.IGNORECASE)
#         if payment_match:
#             payment_terms = payment_match.group(1)

#     # ======================
#     # SAVE TO DATABASE
#     # ======================
#     cursor.execute("""
#         UPDATE vendor_quotes
#         SET
#             unit_price = %s,
#             delivery_time = %s,
#             payment_terms = %s,
#             raw_email = %s,
#             email_received_date = CURRENT_TIMESTAMP,
#             status = 'Quote Received'
#         WHERE rfq_id = %s AND LOWER(vendor_email) = %s
#     """, (
#         unit_price,
#         delivery_days,
#         payment_terms,
#         body,
#         rfq_id,
#         sender_email.lower()
#     ))

#     conn.commit()
#     conn.close()

#     print("Saving to DB:")
#     print("RFQ:", rfq_id)
#     print("Email:", sender_email)
#     print("Price:", unit_price)
#     print("Delivery:", delivery_days)
#     print("Payment:", payment_terms)

#     print("✅ Quote stored successfully")


# # =====================================
# # FETCH RFQ EMAIL REPLIES (IMAP)
# # =====================================

# def fetch_rfq_replies():

#     print("Checking mailbox for RFQ replies...")

#     try:
#         mail = get_gmail_connection()
#         mail.select("inbox")

#         status, messages = mail.search(None, '(UNSEEN SUBJECT "RFQ")')
#         email_ids = messages[0].split()

#         print("Emails found:", len(email_ids))

#         for num in email_ids:

#             status, msg_data = mail.fetch(num, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])

#             subject = msg["subject"]
#             sender = msg["from"]

#             # ======================
#             # RFQ ID EXTRACT
#             # ======================
#             rfq_match = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)

#             if not rfq_match:
#                 continue

#             rfq_id = int(rfq_match.group(1))

#             # ======================
#             # EXTRACT EMAIL
#             # ======================
#             sender_email = re.findall(r'<(.+?)>', sender)
#             sender_email = sender_email[0] if sender_email else sender

#             # ======================
#             # EXTRACT BODY
#             # ======================
#             body = ""

#             if msg.is_multipart():
#                 for part in msg.walk():
#                     if part.get_content_type() == "text/plain":
#                         body = part.get_payload(decode=True).decode(errors="ignore")
#                         break
#             else:
#                 body = msg.get_payload(decode=True).decode(errors="ignore")
                
#             full_text = body
            
#             print("EMAIL BODY:")
#             print(body[:500])

#             print("\n📩 Vendor Reply Found")
#             print("RFQ:", rfq_id)
#             print("Vendor:", sender_email)

#             print("====== FULL EMAIL ======")
#             print(body)
#             print("========================")
            
#             save_quote(rfq_id, sender_email, body)

#         print("✅ Mailbox scan complete")

#     except Exception as e:
#         print("❌ ERROR:", str(e))
#         raise e

import re
import imaplib
import email
import streamlit as st

from services.db import get_connection
from services.ai_extractor import extract_vendor_quote


# =====================================
# GMAIL CONNECTION (IMAP)
# =====================================

def get_gmail_connection():

    EMAIL = st.secrets["EMAIL"]
    APP_PASSWORD = st.secrets["APP_PASSWORD"]

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, APP_PASSWORD)

    return mail


# =====================================
# SAVE VENDOR QUOTE
# =====================================

def save_quote(rfq_id, sender_email, body):

    from services.db import get_cursor

    conn, cursor = get_cursor()

    sender_email = sender_email.strip().lower()

    cursor.execute("""
        SELECT status FROM vendor_quotes
        WHERE rfq_id=%s AND LOWER(vendor_email)=%s
    """, (rfq_id, sender_email.lower()))

    row = cursor.fetchone()

    if not row:
        print("Vendor not found in RFQ list")
        conn.close()
        return

    if row["status"] == "Quote Received":
        print("Quote already processed")
        conn.close()
        return

    print("\n====== FULL EMAIL ======")
    print(body)
    print("========================")

    # ======================
    # AI EXTRACTION
    # ======================
    ai_data = extract_vendor_quote(body)

    unit_price = ai_data.get("unit_price")
    delivery_days = ai_data.get("delivery_days")
    payment_terms = ai_data.get("payment_terms")

    print("AI Extracted:", ai_data)

    # ======================
    # FALLBACK REGEX (STRONG)
    # ======================
    clean_body = body.replace(",", "").replace("\n", " ")

    # PRICE
    if not unit_price:
        price_match = re.search(r'(?:rs\.?|inr)?\s?(\d{3,7})', clean_body, re.IGNORECASE)
        if price_match:
            unit_price = float(price_match.group(1))

    # DELIVERY
    if not delivery_days:
        delivery_match = re.search(r'(\d+)\s*(day|days|week|weeks)', clean_body, re.IGNORECASE)
        if delivery_match:
            delivery_days = delivery_match.group(0)

    # PAYMENT
    if not payment_terms:
        payment_match = re.search(r'(advance|credit|payment\s*\d+\s*days)', clean_body, re.IGNORECASE)
        if payment_match:
            payment_terms = payment_match.group(0)

    print("====== FINAL EXTRACTED ======")
    print("Price:", unit_price)
    print("Delivery:", delivery_days)
    print("Payment:", payment_terms)
    print("============================")

    # ======================
    # SAVE TO DATABASE
    # ======================
    cursor.execute("""
        UPDATE vendor_quotes
        SET
            unit_price = %s,
            delivery_time = %s,
            payment_terms = %s,
            raw_email = %s,
            email_received_date = CURRENT_TIMESTAMP,
            status = 'Quote Received'
        WHERE rfq_id = %s AND LOWER(vendor_email) = %s
    """, (
        unit_price,
        delivery_days,
        payment_terms,
        body,
        rfq_id,
        sender_email
    ))

    conn.commit()
    conn.close()

    print("✅ Quote stored successfully")


# =====================================
# FETCH RFQ EMAIL REPLIES (IMAP)
# =====================================

def fetch_rfq_replies():

    print("Checking mailbox for RFQ replies...")

    try:
        mail = get_gmail_connection()
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN SUBJECT "RFQ")')
        email_ids = messages[0].split()

        print("Emails found:", len(email_ids))

        for num in email_ids:

            status, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            subject = msg["subject"]
            sender = msg["from"]

            # RFQ ID
            rfq_match = re.search(r"RFQ[- ]?(\d+)", subject or "", re.IGNORECASE)
            if not rfq_match:
                continue

            rfq_id = int(rfq_match.group(1))

            # EMAIL
            sender_email = re.findall(r'<(.+?)>', sender or "")
            sender_email = sender_email[0] if sender_email else sender
            sender_email = sender_email.strip().lower()

            # BODY (ROBUST)
            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode(errors="ignore")
                            break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode(errors="ignore")

            print("\n📩 Vendor Reply Found")
            print("RFQ:", rfq_id)
            print("Vendor:", sender_email)

            save_quote(rfq_id, sender_email, body)

        print("✅ Mailbox scan complete")

    except Exception as e:
        print("❌ ERROR:", str(e))
        raise e