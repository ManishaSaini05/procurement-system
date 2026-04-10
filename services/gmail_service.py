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
#correct

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

#     from services.db import get_cursor

#     conn, cursor = get_cursor()

#     sender_email = sender_email.strip().lower()

#     cursor.execute("""
#         SELECT status FROM vendor_quotes
#         WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#     """, (rfq_id, sender_email.lower()))

#     row = cursor.fetchone()

#     if not row:
#         print("Vendor not found in RFQ list")
#         conn.close()
#         return

#     if row["status"] == "Quote Received":
#         print("Quote already processed")
#         conn.close()
#         return

#     print("\n====== FULL EMAIL ======")
#     print(body)
#     print("========================")

#     # ======================
#     # AI EXTRACTION
#     # ======================
#     ai_data = extract_vendor_quote(body)

#     unit_price = ai_data.get("unit_price")
#     delivery_days = ai_data.get("delivery_days")
#     payment_terms = ai_data.get("payment_terms")

#     print("AI Extracted:", ai_data)

#     # ======================
#     # FALLBACK REGEX (STRONG)
#     # ======================
#     clean_body = body.replace(",", "").replace("\n", " ")

#     # PRICE
#     if not unit_price:
#         price_match = re.search(r'(?:rs\.?|inr)?\s?(\d{3,7})', clean_body, re.IGNORECASE)
#         if price_match:
#             unit_price = float(price_match.group(1))

#     # DELIVERY
#     if not delivery_days:
#         delivery_match = re.search(r'(\d+)\s*(day|days|week|weeks)', clean_body, re.IGNORECASE)
#         if delivery_match:
#             delivery_days = delivery_match.group(0)

#     # PAYMENT
#     if not payment_terms:
#         payment_match = re.search(r'(advance|credit|payment\s*\d+\s*days)', clean_body, re.IGNORECASE)
#         if payment_match:
#             payment_terms = payment_match.group(0)

#     print("====== FINAL EXTRACTED ======")
#     print("Price:", unit_price)
#     print("Delivery:", delivery_days)
#     print("Payment:", payment_terms)
#     print("============================")

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
#         sender_email
#     ))

#     conn.commit()
#     conn.close()

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

#             # RFQ ID
#             rfq_match = re.search(r"RFQ[- ]?(\d+)", subject or "", re.IGNORECASE)
#             if not rfq_match:
#                 continue

#             rfq_id = int(rfq_match.group(1))

#             # EMAIL
#             sender_email = re.findall(r'<(.+?)>', sender or "")
#             sender_email = sender_email[0] if sender_email else sender
#             sender_email = sender_email.strip().lower()

#             # BODY (ROBUST)
#             body = ""

#             if msg.is_multipart():
#                 for part in msg.walk():
#                     content_type = part.get_content_type()
#                     content_disposition = str(part.get("Content-Disposition"))

#                     if content_type == "text/plain" and "attachment" not in content_disposition:
#                         payload = part.get_payload(decode=True)
#                         if payload:
#                             body = payload.decode(errors="ignore")
#                             break
#             else:
#                 payload = msg.get_payload(decode=True)
#                 if payload:
#                     body = payload.decode(errors="ignore")

#             print("\n📩 Vendor Reply Found")
#             print("RFQ:", rfq_id)
#             print("Vendor:", sender_email)

#             save_quote(rfq_id, sender_email, body)

#         print("✅ Mailbox scan complete")

#     except Exception as e:
#         print("❌ ERROR:", str(e))
#         raise e

# import re
# import imaplib
# import email
# import streamlit as st

# from services.db import get_cursor
# from services.ai_extractor import extract_vendor_quote


# # =====================================
# # GMAIL CONNECTION (IMAP)
# # =====================================

# def get_gmail_connection():
#     EMAIL = st.secrets["SENDER_EMAIL"]
#     APP_PASSWORD = st.secrets["APP_PASSWORD"]

#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(SENDER_EMAIL, APP_PASSWORD)
#     return mail


# # =====================================
# # SAVE VENDOR QUOTE
# # =====================================

# def save_quote(rfq_id, sender_email, body):

#     sender_email = sender_email.strip().lower()

#     conn, cursor = get_cursor()

#     try:
#         # Check vendor is part of this RFQ
#         cursor.execute("""
#             SELECT status FROM vendor_quotes
#             WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#         """, (rfq_id, sender_email))

#         row = cursor.fetchone()

#         if not row:
#             print(f"Vendor {sender_email} not found in RFQ {rfq_id}")
#             return

#         if row["status"] == "Quote Received":
#             print(f"Quote from {sender_email} for RFQ {rfq_id} already processed")
#             return

#         print(f"\n====== EMAIL BODY — RFQ {rfq_id} from {sender_email} ======")
#         print(body[:500])
#         print("============================================================")

#         # ======================
#         # AI EXTRACTION
#         # ======================
#         ai_data = extract_vendor_quote(body)
#         print("AI Extracted:", ai_data)

#         unit_price   = ai_data.get("unit_price")
#         delivery_days = ai_data.get("delivery_days")
#         payment_terms = ai_data.get("payment_terms")

#         # ======================
#         # FALLBACK REGEX
#         # ======================
#         clean_body = body.replace(",", "").replace("\n", " ")

#         if not unit_price:
#             price_match = re.search(
#                 r'(?:rs\.?|inr|₹)?\s*(\d{3,7})', clean_body, re.IGNORECASE
#             )
#             if price_match:
#                 unit_price = float(price_match.group(1))

#         if not delivery_days:
#             delivery_match = re.search(
#                 r'(\d+)\s*(day|days|week|weeks)', clean_body, re.IGNORECASE
#             )
#             if delivery_match:
#                 delivery_days = delivery_match.group(0)

#         if not payment_terms:
#             payment_match = re.search(
#                 r'(advance|credit|payment\s*\d+\s*days)', clean_body, re.IGNORECASE
#             )
#             if payment_match:
#                 payment_terms = payment_match.group(0)

#         print("Final — Price:", unit_price, "| Delivery:", delivery_days, "| Payment:", payment_terms)

#         # ======================
#         # SAVE TO DATABASE
#         # ======================
#         cursor.execute("""
#             UPDATE vendor_quotes
#             SET
#                 unit_price          = %s,
#                 delivery_time       = %s,
#                 payment_terms       = %s,
#                 raw_email           = %s,
#                 email_received_date = CURRENT_TIMESTAMP,
#                 status              = 'Quote Received'
#             WHERE rfq_id = %s AND LOWER(vendor_email) = %s
#         """, (
#             unit_price,
#             delivery_days,
#             payment_terms,
#             body,
#             rfq_id,
#             sender_email
#         ))

#         conn.commit()
#         print(f"✅ Quote stored for RFQ {rfq_id} from {sender_email}")

#     except Exception as e:
#         print(f"❌ Error saving quote: {e}")
#         conn.rollback()
#         raise e

#     finally:
#         conn.close()


# # =====================================
# # FETCH RFQ EMAIL REPLIES (IMAP)
# # =====================================

# def fetch_rfq_replies():

#     print("Checking mailbox for RFQ replies...")

#     mail = get_gmail_connection()

#     try:
#         mail.select("inbox")

#         status, messages = mail.search(None, '(UNSEEN SUBJECT "RFQ")')
#         email_ids = messages[0].split()
#         print(f"Unread RFQ emails found: {len(email_ids)}")

#         for num in email_ids:

#             status, msg_data = mail.fetch(num, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])

#             subject = msg.get("subject", "")
#             sender  = msg.get("from", "")

#             # Extract RFQ ID from subject
#             rfq_match = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)
#             if not rfq_match:
#                 print(f"Skipping email — no RFQ ID in subject: {subject}")
#                 continue

#             rfq_id = int(rfq_match.group(1))

#             # Extract sender email
#             email_match = re.findall(r'<(.+?)>', sender)
#             sender_email = email_match[0] if email_match else sender
#             sender_email = sender_email.strip().lower()

#             # Extract plain-text body
#             body = ""
#             if msg.is_multipart():
#                 for part in msg.walk():
#                     content_type = part.get_content_type()
#                     disposition  = str(part.get("Content-Disposition", ""))
#                     if content_type == "text/plain" and "attachment" not in disposition:
#                         payload = part.get_payload(decode=True)
#                         if payload:
#                             body = payload.decode(errors="ignore")
#                             break
#             else:
#                 payload = msg.get_payload(decode=True)
#                 if payload:
#                     body = payload.decode(errors="ignore")

#             print(f"\n📩 Processing — RFQ {rfq_id} | Vendor: {sender_email}")
#             save_quote(rfq_id, sender_email, body)

#     finally:
#         mail.logout()

#     print("✅ Mailbox scan complete")

# import re
# import imaplib
# import email
# import pdfplumber
# import io
# import streamlit as st

# from services.db import get_cursor
# from services.ai_extractor import extract_vendor_quote


# # =====================================
# # GMAIL CONNECTION (IMAP)
# # =====================================

# def get_gmail_connection():
#     EMAIL = st.secrets["SENDER_EMAIL"]
#     APP_PASSWORD = st.secrets["APP_PASSWORD"]

#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(EMAIL, APP_PASSWORD)
#     return mail


# # =====================================
# # EXTRACT TEXT FROM PDF BYTES
# # =====================================

# def extract_pdf_text(pdf_bytes):
#     text = ""
#     try:
#         with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
#             for page in pdf.pages:
#                 page_text = page.extract_text()
#                 if page_text:
#                     text += page_text + "\n"
#     except Exception as e:
#         print(f"PDF extraction failed: {e}")
#     return text


# # =====================================
# # EXTRACT FULL TEXT FROM EMAIL
# # (body + any PDF attachments)
# # =====================================

# def extract_email_text(msg):

#     body = ""
#     pdf_text = ""

#     if msg.is_multipart():
#         for part in msg.walk():
#             content_type = part.get_content_type()
#             disposition = str(part.get("Content-Disposition", ""))

#             # Plain text body
#             if content_type == "text/plain" and "attachment" not in disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     body = payload.decode(errors="ignore")

#             # PDF attachment
#             elif content_type == "application/pdf" or (
#                 "attachment" in disposition and disposition.lower().endswith(".pdf")
#             ):
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     print("📎 PDF attachment found — extracting text...")
#                     pdf_text = extract_pdf_text(payload)
#                     print(f"PDF text extracted: {len(pdf_text)} characters")

#             # Some vendors send PDF with generic octet-stream content type
#             elif content_type == "application/octet-stream" and "attachment" in disposition:
#                 filename = part.get_filename() or ""
#                 if filename.lower().endswith(".pdf"):
#                     payload = part.get_payload(decode=True)
#                     if payload:
#                         print("📎 PDF attachment (octet-stream) found — extracting text...")
#                         pdf_text = extract_pdf_text(payload)

#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             body = payload.decode(errors="ignore")

#     # Combine body + PDF text for AI extraction
#     full_text = ""
#     if body:
#         full_text += f"EMAIL BODY:\n{body}\n\n"
#     if pdf_text:
#         full_text += f"PDF ATTACHMENT:\n{pdf_text}\n"

#     return full_text, body, pdf_text


# # =====================================
# # SAVE VENDOR QUOTE
# # =====================================

# def save_quote(rfq_id, sender_email, full_text, raw_body):

#     sender_email = sender_email.strip().lower()

#     conn, cursor = get_cursor()

#     try:
#         # Check vendor is part of this RFQ
#         cursor.execute("""
#             SELECT status FROM vendor_quotes
#             WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#         """, (rfq_id, sender_email))

#         row = cursor.fetchone()

#         if not row:
#             print(f"Vendor {sender_email} not found in RFQ {rfq_id}")
#             return

#         if row["status"] == "Quote Received":
#             print(f"Quote from {sender_email} for RFQ {rfq_id} already processed")
#             return

#         print(f"\n====== PROCESSING RFQ {rfq_id} from {sender_email} ======")
#         print(f"Total text length: {len(full_text)} characters")

#         # ======================
#         # AI EXTRACTION
#         # (uses combined body + PDF text)
#         # ======================
#         ai_data = extract_vendor_quote(full_text)
#         print("AI Extracted:", ai_data)

#         unit_price    = ai_data.get("unit_price")
#         delivery_days = ai_data.get("delivery_days")
#         payment_terms = ai_data.get("payment_terms")

#         # ======================
#         # FALLBACK REGEX
#         # ======================
#         clean_text = full_text.replace(",", "").replace("\n", " ")

#         if not unit_price:
#             price_match = re.search(
#                 r'(?:rs\.?|inr|₹)?\s*(\d{3,7})', clean_text, re.IGNORECASE
#             )
#             if price_match:
#                 unit_price = float(price_match.group(1))

#         if not delivery_days:
#             delivery_match = re.search(
#                 r'(\d+)\s*(day|days|week|weeks)', clean_text, re.IGNORECASE
#             )
#             if delivery_match:
#                 delivery_days = delivery_match.group(0)

#         if not payment_terms:
#             payment_match = re.search(
#                 r'(advance|credit|payment\s*\d+\s*days)', clean_text, re.IGNORECASE
#             )
#             if payment_match:
#                 payment_terms = payment_match.group(0)

#         print("Final — Price:", unit_price, "| Delivery:", delivery_days, "| Payment:", payment_terms)

#         # ======================
#         # SAVE TO DATABASE
#         # ======================
#         cursor.execute("""
#             UPDATE vendor_quotes
#             SET
#                 unit_price          = %s,
#                 delivery_time       = %s,
#                 payment_terms       = %s,
#                 raw_email           = %s,
#                 email_received_date = CURRENT_TIMESTAMP,
#                 status              = 'Quote Received'
#             WHERE rfq_id = %s AND LOWER(vendor_email) = %s
#         """, (
#             unit_price,
#             delivery_days,
#             payment_terms,
#             raw_body,
#             rfq_id,
#             sender_email
#         ))

#         conn.commit()
#         print(f"✅ Quote stored for RFQ {rfq_id} from {sender_email}")

#     except Exception as e:
#         print(f"❌ Error saving quote: {e}")
#         conn.rollback()
#         raise e

#     finally:
#         conn.close()


# # =====================================
# # FETCH RFQ EMAIL REPLIES (IMAP)
# # =====================================

# def fetch_rfq_replies():

#     print("Checking mailbox for RFQ replies...")

#     mail = get_gmail_connection()

#     try:
#         mail.select("inbox")

#         status, messages = mail.search(None, '(UNSEEN SUBJECT "RFQ")')
#         email_ids = messages[0].split()
#         print(f"Unread RFQ emails found: {len(email_ids)}")

#         for num in email_ids:

#             status, msg_data = mail.fetch(num, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])

#             subject = msg.get("subject", "")
#             sender  = msg.get("from", "")

#             # Extract RFQ ID from subject
#             rfq_match = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)
#             if not rfq_match:
#                 print(f"Skipping — no RFQ ID in subject: {subject}")
#                 continue

#             rfq_id = int(rfq_match.group(1))

#             # Extract sender email
#             email_match = re.findall(r'<(.+?)>', sender)
#             sender_email = email_match[0] if email_match else sender
#             sender_email = sender_email.strip().lower()

#             print(f"\n📩 Processing — RFQ {rfq_id} | Vendor: {sender_email}")

#             # Extract body + PDF text
#             full_text, raw_body, pdf_text = extract_email_text(msg)

#             if pdf_text:
#                 print("✅ PDF content included in AI extraction")

#             save_quote(rfq_id, sender_email, full_text, raw_body)

#     finally:
#         mail.logout()

#     print("✅ Mailbox scan complete")

# import re
# import imaplib
# import email
# import pdfplumber
# import io
# import streamlit as st

# from services.db import get_cursor
# from services.ai_extractor import extract_vendor_quote


# # =====================================
# # GMAIL CONNECTION (IMAP)
# # =====================================

# def get_gmail_connection():
#     EMAIL = st.secrets["SENDER_EMAIL"]
#     APP_PASSWORD = st.secrets["SENDER_PASSWORD"]

#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(EMAIL, APP_PASSWORD)
#     return mail


# # =====================================
# # EXTRACT TEXT + TABLES FROM PDF BYTES
# # =====================================

# def extract_pdf_text(pdf_bytes):
#     """
#     Extract both plain text and table data from PDF.
#     Returns a structured string that AI can read easily.
#     """
#     output = ""

#     try:
#         with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
#             for i, page in enumerate(pdf.pages):

#                 output += f"\n--- PAGE {i+1} ---\n"

#                 # Extract plain text
#                 text = page.extract_text()
#                 if text:
#                     output += text + "\n"

#                 # Extract tables separately and format as key:value
#                 tables = page.extract_tables()
#                 for table in tables:
#                     for row in table:
#                         # Filter out empty rows
#                         row_clean = [str(cell).strip() if cell else "" for cell in row]
#                         non_empty = [c for c in row_clean if c]
#                         if len(non_empty) >= 2:
#                             output += " | ".join(non_empty) + "\n"
#                         elif len(non_empty) == 1:
#                             output += non_empty[0] + "\n"

#     except Exception as e:
#         print(f"PDF extraction failed: {e}")

#     return output


# # =====================================
# # EXTRACT FULL TEXT FROM EMAIL
# # (body + any PDF attachments)
# # =====================================

# def extract_email_text(msg):

#     body = ""
#     pdf_text = ""

#     if msg.is_multipart():
#         for part in msg.walk():
#             content_type = part.get_content_type()
#             disposition = str(part.get("Content-Disposition", ""))
#             filename = part.get_filename() or ""

#             # Plain text body
#             if content_type == "text/plain" and "attachment" not in disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     body = payload.decode(errors="ignore")

#             # PDF attachment — check by content type or filename
#             elif (
#                 content_type == "application/pdf"
#                 or filename.lower().endswith(".pdf")
#             ):
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     print(f"📎 PDF found: {filename} — extracting...")
#                     pdf_text = extract_pdf_text(payload)
#                     print(f"PDF extracted: {len(pdf_text)} characters")

#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             body = payload.decode(errors="ignore")

#     # Combine for AI
#     full_text = ""
#     if body:
#         full_text += f"EMAIL BODY:\n{body}\n\n"
#     if pdf_text:
#         full_text += f"PDF QUOTATION:\n{pdf_text}\n"

#     return full_text, body, pdf_text


# # =====================================
# # SAVE VENDOR QUOTE
# # =====================================

# def save_quote(rfq_id, sender_email, full_text, raw_body):

#     sender_email = sender_email.strip().lower()

#     conn, cursor = get_cursor()

#     try:
#         cursor.execute("""
#             SELECT status FROM vendor_quotes
#             WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#         """, (rfq_id, sender_email))

#         row = cursor.fetchone()

#         if not row:
#             print(f"Vendor {sender_email} not found in RFQ {rfq_id}")
#             return

#         if row["status"] == "Quote Received":
#             print(f"Quote from {sender_email} already processed")
#             return

#         print(f"\n====== PROCESSING RFQ {rfq_id} from {sender_email} ======")

#         # AI extraction
#         ai_data = extract_vendor_quote(full_text)
#         print("AI Extracted:", ai_data)

#         unit_price    = ai_data.get("unit_price")
#         delivery_days = ai_data.get("delivery_days")
#         payment_terms = ai_data.get("payment_terms")

#         # Fallback regex on combined text
#         clean_text = full_text.replace(",", "").replace("\n", " ")

#         if not unit_price:
#             # Look specifically for "Unit Price | 4200" pattern in table
#             price_match = re.search(
#                 r'unit\s*price\s*[|:]?\s*(\d{4,7})', clean_text, re.IGNORECASE
#             )
#             if price_match:
#                 unit_price = float(price_match.group(1))

#                  if not delivery_days:
#             delivery_match = re.search(
#                 r'delivery[^|\n]*?(\d+\s*(?:day|days|week|weeks)[^|\n]*)',
#                 clean_text, re.IGNORECASE
#             )
#             if delivery_match:
#                 delivery_days = delivery_match.group(1).strip()

#         if not payment_terms:
#             payment_match = re.search(
#                 r'payment\s*terms?\s*[|:]?\s*([^|\n]+)',
#                 clean_text, re.IGNORECASE
#             )
#             if payment_match:
#                 payment_terms = payment_match.group(1).strip()

#         print("Final — Price:", unit_price, "| Delivery:", delivery_days, "| Payment:", payment_terms)

#         cursor.execute("""
#             UPDATE vendor_quotes
#             SET
#                 unit_price          = %s,
#                 delivery_time       = %s,
#                 payment_terms       = %s,
#                 raw_email           = %s,
#                 email_received_date = CURRENT_TIMESTAMP,
#                 status              = 'Quote Received'
#             WHERE rfq_id = %s AND LOWER(vendor_email) = %s
#         """, (
#             unit_price,
#             delivery_days,
#             payment_terms,
#             raw_body,
#             rfq_id,
#             sender_email
#         ))

#         conn.commit()
#         print(f"✅ Quote stored for RFQ {rfq_id} from {sender_email}")

#     except Exception as e:
#         print(f"❌ Error saving quote: {e}")
#         conn.rollback()
#         raise e

#     finally:
#         conn.close()


# # =====================================
# # FETCH RFQ EMAIL REPLIES (IMAP)
# # =====================================

# def fetch_rfq_replies():

#     print("Checking mailbox for RFQ replies...")

#     mail = get_gmail_connection()

#     try:
#         mail.select("inbox")

#         status, messages = mail.search(None, '(UNSEEN SUBJECT "RFQ")')
#         email_ids = messages[0].split()
#         print(f"Unread RFQ emails found: {len(email_ids)}")

#         for num in email_ids:

#             status, msg_data = mail.fetch(num, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])

#             subject = msg.get("subject", "")
#             sender  = msg.get("from", "")

#             rfq_match = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)
#             if not rfq_match:
#                 print(f"Skipping — no RFQ ID in subject: {subject}")
#                 continue

#             rfq_id = int(rfq_match.group(1))

#             email_match = re.findall(r'<(.+?)>', sender)
#             sender_email = email_match[0] if email_match else sender
#             sender_email = sender_email.strip().lower()

#             print(f"\n📩 Processing — RFQ {rfq_id} | Vendor: {sender_email}")

#             full_text, raw_body, pdf_text = extract_email_text(msg)

#             if pdf_text:
#                 print("✅ PDF content included in extraction")

#             save_quote(rfq_id, sender_email, full_text, raw_body)

#     finally:
#         mail.logout()

#     print("✅ Mailbox scan complete")

# import re
# import imaplib
# import email
# import pdfplumber
# import io
# import streamlit as st

# from services.db import get_cursor
# from services.ai_extractor import extract_vendor_quote


# # =====================================
# # GMAIL CONNECTION
# # =====================================

# def get_gmail_connection():
#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(st.secrets["SENDER_EMAIL"], st.secrets["SENDER_PASSWORD"])
#     return mail


# # =====================================
# # EXTRACT TEXT + TABLES FROM PDF
# # =====================================

# def extract_pdf_text(pdf_bytes):
#     output = ""
#     try:
#         with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
#             for i, page in enumerate(pdf.pages):
#                 output += f"\n--- PAGE {i+1} ---\n"

#                 # Plain text
#                 text = page.extract_text()
#                 if text:
#                     output += text + "\n"

#                 # Tables formatted as rows
#                 tables = page.extract_tables()
#                 for table in tables:
#                     output += "\n[TABLE]\n"
#                     for row in table:
#                         row_clean = [str(cell).strip() if cell else "" for cell in row]
#                         non_empty = [c for c in row_clean if c]
#                         if non_empty:
#                             output += " | ".join(non_empty) + "\n"
#                     output += "[/TABLE]\n"

#     except Exception as e:
#         print(f"PDF extraction error: {e}")
#     return output


# # =====================================
# # EXTRACT TEXT FROM EMAIL
# # =====================================

# def extract_email_text(msg):
#     body = ""
#     pdf_text = ""

#     if msg.is_multipart():
#         for part in msg.walk():
#             content_type = part.get_content_type()
#             disposition  = str(part.get("Content-Disposition", ""))
#             filename     = part.get_filename() or ""

#             if content_type == "text/plain" and "attachment" not in disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     body = payload.decode(errors="ignore")

#             elif content_type == "application/pdf" or filename.lower().endswith(".pdf"):
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     print(f"📎 PDF found: {filename}")
#                     pdf_text = extract_pdf_text(payload)
#                     print(f"PDF text length: {len(pdf_text)}")
#                     print("PDF CONTENT PREVIEW:\n", pdf_text[:500])
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             body = payload.decode(errors="ignore")

#     full_text = ""
#     if body:
#         full_text += f"EMAIL BODY:\n{body}\n\n"
#     if pdf_text:
#         full_text += f"PDF QUOTATION:\n{pdf_text}\n"

#     return full_text, body, pdf_text


# # =====================================
# # SAVE VENDOR QUOTE
# # =====================================

# def save_quote(rfq_id, sender_email, full_text, raw_body):
#     sender_email = sender_email.strip().lower()

#     conn, cursor = get_cursor()
#     try:
#         cursor.execute("""
#             SELECT status FROM vendor_quotes
#             WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#         """, (rfq_id, sender_email))

#         row = cursor.fetchone()

#         if not row:
#             print(f"Vendor {sender_email} not found in RFQ {rfq_id}")
#             return

#         if row["status"] == "Quote Received":
#             print(f"Already processed: RFQ {rfq_id} from {sender_email}")
#             return

#         print(f"\n====== PROCESSING RFQ {rfq_id} | {sender_email} ======")
#         print("FULL TEXT SENT TO EXTRACTOR:\n", full_text[:1000])

#         extracted = extract_vendor_quote(full_text)
#         print("EXTRACTED:", extracted)

#         unit_price    = extracted.get("unit_price")
#         delivery_days = extracted.get("delivery_days")
#         payment_terms = extracted.get("payment_terms")

#         cursor.execute("""
#             UPDATE vendor_quotes
#             SET
#                 unit_price          = %s,
#                 delivery_time       = %s,
#                 payment_terms       = %s,
#                 raw_email           = %s,
#                 email_received_date = CURRENT_TIMESTAMP,
#                 status              = 'Quote Received'
#             WHERE rfq_id = %s AND LOWER(vendor_email) = %s
#         """, (unit_price, delivery_days, payment_terms, raw_body, rfq_id, sender_email))

#         conn.commit()
#         print(f"✅ Saved — Price:{unit_price} | Delivery:{delivery_days} | Payment:{payment_terms}")

#     except Exception as e:
#         conn.rollback()
#         print(f"❌ Error: {e}")
#         raise e
#     finally:
#         conn.close()


# # =====================================
# # FETCH RFQ REPLIES
# # =====================================

# def fetch_rfq_replies():
#     print("Checking mailbox...")
#     mail = get_gmail_connection()

#     try:
#         mail.select("inbox")
#         status, messages = mail.search(None, '(UNSEEN SUBJECT "RFQ")')
#         email_ids = messages[0].split()
#         print(f"Found {len(email_ids)} unread RFQ emails")

#         for num in email_ids:
#             status, msg_data = mail.fetch(num, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])

#             subject = msg.get("subject", "")
#             sender  = msg.get("from", "")

#             rfq_match = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)
#             if not rfq_match:
#                 print(f"Skipping — no RFQ ID in: {subject}")
#                 continue

#             rfq_id = int(rfq_match.group(1))

#             email_match = re.findall(r'<(.+?)>', sender)
#             sender_email = (email_match[0] if email_match else sender).strip().lower()

#             print(f"\n📩 RFQ {rfq_id} | {sender_email}")

#             full_text, raw_body, pdf_text = extract_email_text(msg)
#             save_quote(rfq_id, sender_email, full_text, raw_body)

#     finally:
#         mail.logout()

#     print("✅ Done")

# New version #

# import re
# import imaplib
# import email
# import pdfplumber
# import io
# import streamlit as st

# from services.db import get_cursor
# from services.ai_extractor import extract_vendor_quote


# def get_gmail_connection():
#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(st.secrets["SENDER_EMAIL"], st.secrets["SENDER_PASSWORD"])
#     return mail


# def extract_pdf_text(pdf_bytes):
#     output = ""
#     try:
#         with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
#             for i, page in enumerate(pdf.pages):
#                 output += f"\n--- PAGE {i+1} ---\n"
#                 text = page.extract_text()
#                 if text:
#                     output += text + "\n"
#                 for table in page.extract_tables():
#                     output += "\n[TABLE]\n"
#                     for row in table:
#                         clean = [str(c).strip() if c else "" for c in row]
#                         non_empty = [c for c in clean if c]
#                         if non_empty:
#                             output += " | ".join(non_empty) + "\n"
#                     output += "[/TABLE]\n"
#     except Exception as e:
#         print(f"PDF read error: {e}")
#     return output


# def extract_email_content(msg):
#     body     = ""
#     pdf_text = ""

#     if msg.is_multipart():
#         for part in msg.walk():
#             ctype       = part.get_content_type()
#             disposition = str(part.get("Content-Disposition", ""))
#             filename    = part.get_filename() or ""

#             if ctype == "text/plain" and "attachment" not in disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     body = payload.decode(errors="ignore")

#             elif ctype == "application/pdf" or filename.lower().endswith(".pdf"):
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     print(f"PDF found: {filename}")
#                     pdf_text = extract_pdf_text(payload)
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             body = payload.decode(errors="ignore")

#     full_text = ""
#     if body:
#         full_text += f"EMAIL BODY:\n{body}\n\n"
#     if pdf_text:
#         full_text += f"PDF QUOTATION:\n{pdf_text}\n"

#     return full_text, body


# def save_quote(rfq_id, sender_email, full_text, raw_body):
#     sender_email = sender_email.strip().lower()
#     conn, cursor = get_cursor()
#     try:
#         cursor.execute("""
#             SELECT status, round FROM vendor_quotes
#             WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#             ORDER BY round DESC LIMIT 1
#         """, (rfq_id, sender_email))
#         row = cursor.fetchone()

#         if not row:
#             print(f"Vendor {sender_email} not in RFQ {rfq_id}")
#             return

#         current_round = row["round"] or 1

#         # If already received, this is a re-negotiation reply — increment round
#         if row["status"] == "Quote Received":
#             current_round += 1
#             print(f"Re-negotiation reply — round {current_round}")

#         extracted = extract_vendor_quote(full_text)
#         print(f"Extracted: {extracted}")

#         unit_price    = extracted.get("unit_price")
#         delivery_days = extracted.get("delivery_days")
#         payment_terms = extracted.get("payment_terms")

#         if row["status"] == "Quote Received":
#             # Insert a new round row
#             cursor.execute("""
#                 INSERT INTO vendor_quotes
#                     (rfq_id, vendor_name, vendor_email, unit_price,
#                      delivery_time, payment_terms, raw_email,
#                      email_received_date, status, round)
#                 SELECT rfq_id, vendor_name, vendor_email,
#                        %s, %s, %s, %s, CURRENT_TIMESTAMP, 'Quote Received', %s
#                 FROM vendor_quotes
#                 WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#                 ORDER BY round DESC LIMIT 1
#             """, (unit_price, delivery_days, payment_terms,
#                   raw_body, current_round, rfq_id, sender_email))
#         else:
#             cursor.execute("""
#                 UPDATE vendor_quotes
#                 SET unit_price=%s, delivery_time=%s, payment_terms=%s,
#                     raw_email=%s, email_received_date=CURRENT_TIMESTAMP,
#                     status='Quote Received', round=%s
#                 WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#             """, (unit_price, delivery_days, payment_terms,
#                   raw_body, current_round, rfq_id, sender_email))

#         # Mark reverse RFQ as replied
#         cursor.execute("""
#             UPDATE reverse_rfq SET reply_received=TRUE
#             WHERE rfq_id=%s AND LOWER(vendor_email)=%s AND reply_received=FALSE
#         """, (rfq_id, sender_email))

#         conn.commit()
#         print(f"Saved — RFQ {rfq_id} | {sender_email} | Round {current_round}")

#     except Exception as e:
#         conn.rollback()
#         print(f"Error saving quote: {e}")
#         raise e
#     finally:
#         conn.close()


# def fetch_rfq_replies():
#     print("Scanning inbox...")
#     mail = get_gmail_connection()
#     try:
#         mail.select("inbox")
#         _, messages = mail.search(None, '(UNSEEN SUBJECT "RFQ")')
#         ids = messages[0].split()
#         print(f"Found {len(ids)} unread RFQ emails")

#         for num in ids:
#             _, msg_data = mail.fetch(num, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])

#             subject = msg.get("subject", "")
#             sender  = msg.get("from", "")

#             m = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)
#             if not m:
#                 print(f"No RFQ ID in: {subject}")
#                 continue

#             rfq_id = int(m.group(1))

#             em = re.findall(r'<(.+?)>', sender)
#             sender_email = (em[0] if em else sender).strip().lower()

#             print(f"Processing RFQ-{rfq_id} from {sender_email}")
#             full_text, raw_body = extract_email_content(msg)
#             save_quote(rfq_id, sender_email, full_text, raw_body)

#     finally:
#         mail.logout()
#     print("Inbox scan complete.")

# import re
# import imaplib
# import email
# import pdfplumber
# import io
# import streamlit as st

# from services.db import get_cursor
# from services.ai_extractor import extract_vendor_quote


# def get_gmail_connection():
#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(st.secrets["SENDER_EMAIL"], st.secrets["SENDER_PASSWORD"])
#     return mail


# def extract_pdf_text(pdf_bytes):
#     output = ""
#     try:
#         with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
#             for i, page in enumerate(pdf.pages):
#                 output += f"\n--- PAGE {i+1} ---\n"
#                 text = page.extract_text()
#                 if text:
#                     output += text + "\n"
#                 for table in page.extract_tables():
#                     output += "\n[TABLE]\n"
#                     for row in table:
#                         clean = [str(c).strip() if c else "" for c in row]
#                         non_empty = [c for c in clean if c]
#                         if non_empty:
#                             output += " | ".join(non_empty) + "\n"
#                     output += "[/TABLE]\n"
#     except Exception as e:
#         print(f"PDF read error: {e}")
#     return output


# def extract_email_content(msg):
#     body     = ""
#     pdf_text = ""

#     if msg.is_multipart():
#         for part in msg.walk():
#             ctype       = part.get_content_type()
#             disposition = str(part.get("Content-Disposition", ""))
#             filename    = part.get_filename() or ""

#             # if ctype == "text/plain" and "attachment" not in disposition:
#             #     payload = part.get_payload(decode=True)
#             #     if payload:
#             #         body = payload.decode(errors="ignore")
#             if ctype == "text/plain" and "attachment" not in disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     body = payload.decode(errors="ignore")

#             elif ctype == "text/html" and "attachment" not in disposition and not body:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     # Strip HTML tags for plain text
#                     import re as re2
#                     html = payload.decode(errors="ignore")
#                     body = re2.sub(r'<[^>]+>', ' ', html)
#                     body = re2.sub(r'\s+', ' ', body).strip()

#             elif ctype == "application/pdf" or filename.lower().endswith(".pdf"):
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     print(f"PDF found: {filename}")
#                     pdf_text = extract_pdf_text(payload)
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             body = payload.decode(errors="ignore")

#     full_text = ""
#     if body:
#         full_text += f"EMAIL BODY:\n{body}\n\n"
#     if pdf_text:
#         full_text += f"PDF QUOTATION:\n{pdf_text}\n"

#     return full_text, body


# def get_pending_rfqs():
#     """
#     Get all RFQ IDs and vendor emails that are still in 'RFQ Sent' status.
#     We will search emails for these specifically.
#     """
#     conn, cursor = get_cursor()
#     try:
#         cursor.execute("""
#             SELECT 
#                 vq.rfq_id,
#                 vq.vendor_email,
#                 vq.vendor_name,
#                 vq.status
#             FROM vendor_quotes vq
#             WHERE vq.status = 'RFQ Sent'
#             ORDER BY vq.rfq_id DESC
#         """)
#         return cursor.fetchall()
#     finally:
#         conn.close()


# def save_quote(rfq_id, sender_email, full_text, raw_body):
#     print(f"FULL TEXT LENGTH: {len(full_text)}")
#     print(f"RAW BODY LENGTH: {len(raw_body)}")
#     print(f"FULL TEXT PREVIEW: {full_text[:500]}")
#     sender_email = sender_email.strip().lower()
#     conn, cursor = get_cursor()
#     try:
#         cursor.execute("""
#             SELECT status, round FROM vendor_quotes
#             WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#             ORDER BY round DESC LIMIT 1
#         """, (rfq_id, sender_email))
#         row = cursor.fetchone()

#         if not row:
#             print(f"Vendor {sender_email} not in RFQ {rfq_id}")
#             return False

#         if row["status"] == "Quote Received":
#             print(f"Already processed: RFQ {rfq_id} from {sender_email}")
#             return False

#         extracted = extract_vendor_quote(full_text)
#         print(f"Extracted: {extracted}")

#         unit_price    = extracted.get("unit_price")
#         delivery_days = extracted.get("delivery_days")
#         payment_terms = extracted.get("payment_terms")

#         cursor.execute("""
#             UPDATE vendor_quotes
#             SET unit_price=%s, delivery_time=%s, payment_terms=%s,
#                 raw_email=%s, email_received_date=CURRENT_TIMESTAMP,
#                 status='Quote Received'
#             WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#         """, (unit_price, delivery_days, payment_terms,
#               raw_body, rfq_id, sender_email))

#         conn.commit()
#         print(f"Saved — RFQ {rfq_id} | {sender_email} | Price: {unit_price}")
#         return True

#     except Exception as e:
#         conn.rollback()
#         print(f"Error saving quote: {e}")
#         raise e
#     finally:
#         conn.close()


# def fetch_rfq_replies():
#     print("Scanning inbox for RFQ replies...")

#     # Get all pending RFQ vendor emails from database
#     pending = get_pending_rfqs()
#     if not pending:
#         print("No pending RFQs found.")
#         return

#     print(f"Pending RFQs to check: {len(pending)}")
#     for p in pending:
#         print(f"  RFQ-{p['rfq_id']} | {p['vendor_name']} | {p['vendor_email']}")

#     mail = get_gmail_connection()
#     processed = 0

#     try:
#         mail.select("inbox")

#         # Search ALL emails with RFQ in subject — not just unseen
#         _, messages = mail.search(None, 'SUBJECT "RFQ"')
        
#         all_ids = messages[0].split()
#         print(f"Total emails with RFQ in subject: {len(all_ids)}")

#         # Build lookup: rfq_id -> list of vendor emails pending
#         pending_map = {}
#         for p in pending:
#             rfq_id = p["rfq_id"]
#             if rfq_id not in pending_map:
#                 pending_map[rfq_id] = []
#             pending_map[rfq_id].append(p["vendor_email"].strip().lower())

#         for num in all_ids:
#             _, msg_data = mail.fetch(num, "(RFC822)")
#             msg = email.message_from_bytes(msg_data[0][1])

#             subject = msg.get("subject", "")
#             sender  = msg.get("from", "")

#             # Extract RFQ ID from subject
#             # m = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)
#             m = re.search(r"RFQ[\-\—\– ]?(\d+)", subject, re.IGNORECASE)
#             if not m:
#                 continue

#             rfq_id = int(m.group(1))

#             # Only process if this RFQ has pending vendors
#             if rfq_id not in pending_map:
#                 continue

#             # Extract sender email
#             em = re.findall(r'<(.+?)>', sender)
#             sender_email = (em[0] if em else sender).strip().lower()

#             # Only process if this vendor email is pending for this RFQ
#             # if sender_email not in pending_map[rfq_id]:
#             #     print(f"Skipping — {sender_email} not in pending list for RFQ-{rfq_id}")
#             #     continue
#             matched = False
#             for db_email in pending_map[rfq_id]:
#                if db_email in sender_email or sender_email in db_email:
#                     matched = True
#                     sender_email = db_email  # normalize
#                     break

#             if not matched:
#                 print(f"Skipping — {sender_email} not matched for RFQ-{rfq_id}")
#                 continue

#             print(f"\nProcessing RFQ-{rfq_id} from {sender_email}")
#             full_text, raw_body = extract_email_content(msg)
#             saved = save_quote(rfq_id, sender_email, full_text, raw_body)
#             if saved:
#                 processed += 1
#                 # Remove from pending so we don't process duplicates
#                 pending_map[rfq_id].remove(sender_email)

#     finally:
#         mail.logout()

#     print(f"Done. Processed {processed} new quote(s).")

# import re
# import imaplib
# import email
# import email.header
# import pdfplumber
# import io
# import streamlit as st

# from services.db import get_cursor
# from services.ai_extractor import extract_vendor_quote


# def get_gmail_connection():
#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(st.secrets["SENDER_EMAIL"], st.secrets["SENDER_PASSWORD"])
#     return mail


# def decode_subject(subject):
#     """Decode email subject which may be encoded."""
#     if not subject:
#         return ""
#     decoded_parts = email.header.decode_header(subject)
#     subject_str = ""
#     for part, encoding in decoded_parts:
#         if isinstance(part, bytes):
#             subject_str += part.decode(encoding or "utf-8", errors="ignore")
#         else:
#             subject_str += str(part)
#     return subject_str


# def extract_sender_email(from_field):
#     """Extract clean email address from From field."""
#     if not from_field:
#         return ""
#     # Try <email> format first
#     match = re.findall(r'<(.+?)>', from_field)
#     if match:
#         return match[0].strip().lower()
#     # Fallback: whole field
#     return from_field.strip().lower()


# def extract_pdf_text(pdf_bytes):
#     output = ""
#     try:
#         with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
#             for i, page in enumerate(pdf.pages):
#                 output += f"\n--- PAGE {i+1} ---\n"
#                 text = page.extract_text()
#                 if text:
#                     output += text + "\n"
#                 for table in page.extract_tables():
#                     output += "\n[TABLE]\n"
#                     for row in table:
#                         clean = [str(c).strip() if c else "" for c in row]
#                         non_empty = [c for c in clean if c]
#                         if non_empty:
#                             output += " | ".join(non_empty) + "\n"
#                     output += "[/TABLE]\n"
#     except Exception as e:
#         print(f"PDF error: {e}")
#     return output


# def extract_email_content(msg):
#     body     = ""
#     pdf_text = ""

#     if msg.is_multipart():
#         for part in msg.walk():
#             ctype       = part.get_content_type()
#             disposition = str(part.get("Content-Disposition", ""))
#             filename    = part.get_filename() or ""

#             if ctype == "text/plain" and "attachment" not in disposition:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     body = payload.decode(errors="ignore")

#             elif ctype == "text/html" and "attachment" not in disposition and not body:
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     html = payload.decode(errors="ignore")
#                     body = re.sub(r'<[^>]+>', ' ', html)
#                     body = re.sub(r'\s+', ' ', body).strip()

#             elif ctype == "application/pdf" or filename.lower().endswith(".pdf"):
#                 payload = part.get_payload(decode=True)
#                 if payload:
#                     print(f"  PDF attachment: {filename}")
#                     pdf_text = extract_pdf_text(payload)
#     else:
#         payload = msg.get_payload(decode=True)
#         if payload:
#             body = payload.decode(errors="ignore")

#     full_text = ""
#     if body:
#         full_text += f"EMAIL BODY:\n{body}\n\n"
#     if pdf_text:
#         full_text += f"PDF QUOTATION:\n{pdf_text}\n"

#     return full_text, body


# # def get_pending_rfqs():
# #     """Return all vendor_quotes rows still in RFQ Sent status."""
# #     conn, cursor = get_cursor()
# #     try:
# #         cursor.execute("""
# #             SELECT vq.rfq_id, vq.vendor_email, vq.vendor_name
# #             FROM vendor_quotes vq
# #             WHERE vq.status = 'RFQ Sent'
# #             ORDER BY vq.rfq_id DESC
# #         """)
# #         return cursor.fetchall()
# #     finally:
# #         conn.close()
# def get_pending_rfqs():
#     """
#     Fetch ALL active vendor quotes — both RFQ Sent and Quote Received.
#     Quote Received included so revised quotes can be fetched.
#     """
#     conn, cursor = get_cursor()
#     try:
#         cursor.execute("""
#             SELECT vq.rfq_id, vq.vendor_email, vq.vendor_name
#             FROM vendor_quotes vq
#             WHERE vq.status IN ('RFQ Sent', 'Quote Received')
#             ORDER BY vq.rfq_id DESC
#         """)
#         return cursor.fetchall()
#     finally:
#         conn.close()


# def save_quote(rfq_id, sender_email, full_text, raw_body):
#     sender_email = sender_email.strip().lower()
#     conn, cursor = get_cursor()
#     try:
#         cursor.execute("""
#             SELECT id, status FROM vendor_quotes
#             WHERE rfq_id=%s AND LOWER(vendor_email)=%s
#             ORDER BY id DESC LIMIT 1
#         """, (rfq_id, sender_email))
#         row = cursor.fetchone()

#         if not row:
#             print(f"  No DB match: rfq_id={rfq_id} vendor={sender_email}")
#             return False

#         # if row["status"] == "Quote Received":
#         #     print(f"  Already processed: rfq_id={rfq_id} vendor={sender_email}")
#         #     return False
#         # Always update — even if already received (handles revised quotes)
#         print(f"  Updating quote (status was: {row['status']})")

#         print(f"  Extracting from email body ({len(raw_body)} chars)...")
#         extracted = extract_vendor_quote(full_text)
#         print(f"  Result: {extracted}")

#         cursor.execute("""
#             UPDATE vendor_quotes
#             SET unit_price          = %s,
#                 delivery_time       = %s,
#                 payment_terms       = %s,
#                 raw_email           = %s,
#                 email_received_date = CURRENT_TIMESTAMP,
#                 status              = 'Quote Received'
#             WHERE rfq_id = %s AND LOWER(vendor_email) = %s
#         """, (
#             extracted.get("unit_price"),
#             extracted.get("delivery_days"),
#             extracted.get("payment_terms"),
#             raw_body, rfq_id, sender_email
#         ))
#         conn.commit()
#         print(f"  SAVED successfully.")
#         return True

#     except Exception as e:
#         conn.rollback()
#         print(f"  Save error: {e}")
#         raise e
#     finally:
#         conn.close()


# def fetch_rfq_replies():
#     print("\n======== FETCH RFQ REPLIES START ========")

#     pending = get_pending_rfqs()
#     print(f"Pending RFQs in DB: {len(pending)}")
#     for p in pending:
#         print(f"  RFQ-{p['rfq_id']} | {p['vendor_name']} | {p['vendor_email']}")

#     if not pending:
#         print("Nothing pending. Done.")
#         return

#     # Build lookup: vendor_email_lower -> rfq_id
#     # email_to_rfq = {
#     #     p["vendor_email"].strip().lower(): p["rfq_id"]
#     #     for p in pending
#     # }
#     # # Build lookup: rfq_id -> vendor_email
#     # rfq_to_email = {
#     #     p["rfq_id"]: p["vendor_email"].strip().lower()
#     #     for p in pending
#     # }

#     # print(f"\nLooking for emails from: {list(email_to_rfq.keys())}")
#     # Build lookup: vendor_email_lower -> rfq_id
#    # Build lookup: rfq_id -> vendor_email
#     rfq_to_email = {
#         p["rfq_id"]: p["vendor_email"].strip().lower()
#         for p in pending
#     }
#     pending_rfq_ids = set(rfq_to_email.keys())
#     print(f"\nPending RFQ IDs: {sorted(pending_rfq_ids)}")

#     mail = get_gmail_connection()
#     processed = 0

#     try:
#         mail.select('"[Gmail]/All Mail"')

#         # Search ALL emails - no filter - so we never miss anything
#         _, messages = mail.search(None, "ALL")
#         all_ids = messages[0].split()
#         print(f"Total emails in inbox: {len(all_ids)}")

#         # Only check last 100 emails to avoid timeout
#         check_ids = all_ids[-100:]
#         print(f"Checking last {len(check_ids)} emails...")

#         for num in check_ids:
#             try:
#                 _, msg_data = mail.fetch(num, "(RFC822)")
#                 msg = email.message_from_bytes(msg_data[0][1])

#                 subject      = decode_subject(msg.get("subject", ""))
#                 from_field   = msg.get("from", "")
#                 sender_email = extract_sender_email(from_field)

#                 print(f"\n  Subject : {subject}")
#                 print(f"  From    : {from_field}")
#                 print(f"  Parsed  : {sender_email}")

#                 # matched_rfq_id = None

#                 # # Method 1: Match by sender email
#                 # if sender_email in email_to_rfq:
#                 #     matched_rfq_id = email_to_rfq[sender_email]
#                 #     print(f"  MATCH by sender email -> RFQ-{matched_rfq_id}")

#                 # # Method 2: Match by RFQ ID in subject
#                 # if not matched_rfq_id:
#                 #     m = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)
#                 #     if m:
#                 #         subject_rfq_id = int(m.group(1))
#                 #         if subject_rfq_id in rfq_to_email:
#                 #             matched_rfq_id = subject_rfq_id
#                 #             print(f"  MATCH by RFQ ID in subject -> RFQ-{matched_rfq_id}")
#                 #             # Use the stored vendor email for saving
#                 #             sender_email = rfq_to_email[subject_rfq_id]

#                 # if not matched_rfq_id:
#                 #     print(f"  NO MATCH — skipping")
#                 #     continue
#                 matched_rfq_id = None

# # Match ONLY by RFQ ID in subject — most reliable method
# # Do NOT match by sender email alone as one person may send multiple RFQs
#                 m = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)
#                 if m:
#                     subject_rfq_id = int(m.group(1))
#                     if subject_rfq_id in pending_rfq_ids:
#         # Only accept if it is a REPLY (subject starts with Re:)
#                         if subject.strip().lower().startswith("re:"):
#                             matched_rfq_id = subject_rfq_id
#                             sender_email   = rfq_to_email[subject_rfq_id]
#                             print(f"  MATCH by RFQ ID in subject (reply) -> RFQ-{matched_rfq_id}")
#                         else:
#                             print(f"  SKIP — RFQ-{subject_rfq_id} found but not a reply (no Re:)")
#                     else:
#                         print(f"  SKIP — RFQ-{subject_rfq_id} not in pending list")
#                 else:
#                    print(f"  SKIP — no RFQ ID in subject")

#                 if not matched_rfq_id:
#                     continue

#                 full_text, raw_body = extract_email_content(msg)
#                 print(f"  Body length: {len(raw_body)}")

#                 saved = save_quote(matched_rfq_id, sender_email, full_text, raw_body)
#                 if saved:
#                     processed += 1

#             except Exception as e:
#                 print(f"  Error processing email: {e}")
#                 continue

#     finally:
#         mail.logout()

#     print(f"\n======== DONE — {processed} quote(s) saved ========\n")
#     return processed

import re
import imaplib
import email
import email.header
import pdfplumber
import io
import streamlit as st

from services.db import get_cursor
from services.ai_extractor import extract_vendor_quote


def get_gmail_connection():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(st.secrets["SENDER_EMAIL"], st.secrets["SENDER_PASSWORD"])
    return mail


def decode_subject(subject):
    if not subject:
        return ""
    decoded_parts = email.header.decode_header(subject)
    subject_str = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            subject_str += part.decode(encoding or "utf-8", errors="ignore")
        else:
            subject_str += str(part)
    return subject_str


def extract_sender_email(from_field):
    if not from_field:
        return ""
    match = re.findall(r'<(.+?)>', from_field)
    if match:
        return match[0].strip().lower()
    return from_field.strip().lower()


def extract_pdf_text(pdf_bytes):
    output = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                output += f"\n--- PAGE {i+1} ---\n"
                text = page.extract_text()
                if text:
                    output += text + "\n"
                for table in page.extract_tables():
                    output += "\n[TABLE]\n"
                    for row in table:
                        clean = [str(c).strip() if c else "" for c in row]
                        non_empty = [c for c in clean if c]
                        if non_empty:
                            output += " | ".join(non_empty) + "\n"
                    output += "[/TABLE]\n"
    except Exception as e:
        print(f"PDF error: {e}")
    return output


def extract_email_content(msg):
    body     = ""
    pdf_text = ""

    if msg.is_multipart():
        for part in msg.walk():
            ctype       = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            filename    = part.get_filename() or ""

            if ctype == "text/plain" and "attachment" not in disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(errors="ignore")

            elif ctype == "text/html" and "attachment" not in disposition and not body:
                payload = part.get_payload(decode=True)
                if payload:
                    html = payload.decode(errors="ignore")
                    body = re.sub(r'<[^>]+>', ' ', html)
                    body = re.sub(r'\s+', ' ', body).strip()

            elif ctype == "application/pdf" or filename.lower().endswith(".pdf"):
                payload = part.get_payload(decode=True)
                if payload:
                    print(f"  PDF attachment: {filename}")
                    pdf_text = extract_pdf_text(payload)

                    print(f"  PDF found: {filename} ({len(payload)} bytes)")
                    pdf_text = extract_pdf_text(payload)
                    print(f"  PDF text extracted: {len(pdf_text)} chars")
                    print(f"  PDF preview: {pdf_text[:300]}")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(errors="ignore")

    full_text = ""
    if body:
        full_text += f"EMAIL BODY:\n{body}\n\n"
    if pdf_text:
        full_text += f"PDF QUOTATION:\n{pdf_text}\n"

    return full_text, body


def get_active_rfqs():
    """Fetch all RFQ Sent + Quote Received vendor quotes."""
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT vq.rfq_id, vq.vendor_email, vq.vendor_name, 
                   vq.status, vq.email_message_id
            FROM vendor_quotes vq
            WHERE vq.status IN ('RFQ Sent', 'Quote Received')
            ORDER BY vq.rfq_id DESC
        """)
        return cursor.fetchall()
    finally:
        conn.close()


def is_already_processed(rfq_id, message_id):
    """Check if this exact email was already saved."""
    if not message_id:
        return False
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT id FROM vendor_quotes
            WHERE rfq_id=%s AND email_message_id=%s
        """, (rfq_id, message_id))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def save_quote(rfq_id, sender_email, full_text, raw_body, message_id):
    sender_email = sender_email.strip().lower()
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT id, status FROM vendor_quotes
            WHERE rfq_id=%s AND LOWER(vendor_email)=%s
            ORDER BY id DESC LIMIT 1
        """, (rfq_id, sender_email))
        row = cursor.fetchone()

        if not row:
            print(f"  No DB match: rfq_id={rfq_id} vendor={sender_email}")
            return False

        print(f"  Updating quote for RFQ-{rfq_id} (was: {row['status']})")
        print(f"  Extracting from {len(raw_body)} chars...")

        extracted = extract_vendor_quote(full_text)
        print(f"  Extracted: {extracted}")

        cursor.execute("""
            UPDATE vendor_quotes
            SET unit_price          = %s,
                delivery_time       = %s,
                payment_terms       = %s,
                raw_email           = %s,
                email_received_date = CURRENT_TIMESTAMP,
                status              = 'Quote Received',
                email_message_id    = %s
            WHERE rfq_id = %s AND LOWER(vendor_email) = %s
        """, (
            extracted.get("unit_price"),
            extracted.get("delivery_days"),
            extracted.get("payment_terms"),
            raw_body,
            message_id,
            rfq_id,
            sender_email
        ))
        conn.commit()
        print(f"  SAVED: Price={extracted.get('unit_price')} | Delivery={extracted.get('delivery_days')} | Payment={extracted.get('payment_terms')}")
        return True

    except Exception as e:
        conn.rollback()
        print(f"  Save error: {e}")
        raise e
    finally:
        conn.close()


def fetch_rfq_replies():
    print("\n======== FETCH RFQ REPLIES START ========")

    active = get_active_rfqs()
    print(f"Active RFQs in DB: {len(active)}")
    for p in active:
        print(f"  RFQ-{p['rfq_id']} | {p['vendor_name']} | {p['vendor_email']} | {p['status']}")

    if not active:
        print("No active RFQs. Done.")
        return 0

    # Build lookup: rfq_id -> vendor_email
    rfq_to_email = {
        p["rfq_id"]: p["vendor_email"].strip().lower()
        for p in active
    }
    # Track already processed message IDs per rfq
    processed_msg_ids = {
        p["rfq_id"]: p["email_message_id"]
        for p in active
    }

    pending_rfq_ids = set(rfq_to_email.keys())
    print(f"\nWatching RFQ IDs: {sorted(pending_rfq_ids)}")

    mail = get_gmail_connection()
    processed = 0

    try:
        mail.select('"[Gmail]/All Mail"')

        _, messages = mail.search(None, "ALL")
        all_ids = messages[0].split()
        print(f"Total emails found: {len(all_ids)}")

        # Check last 200 emails
        check_ids = all_ids[-200:]
        print(f"Checking last {len(check_ids)} emails...")

        for num in check_ids:
            try:
                _, msg_data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                subject    = decode_subject(msg.get("subject", ""))
                from_field = msg.get("from", "")
                message_id = msg.get("message-id", "").strip()

                sender_email = extract_sender_email(from_field)

                # Only process replies (subject starts with Re:)
                if not subject.strip().lower().startswith("re:"):
                    continue

                # Must have RFQ ID in subject
                m = re.search(r"RFQ[- ]?(\d+)", subject, re.IGNORECASE)
                if not m:
                    continue

                subject_rfq_id = int(m.group(1))

                if subject_rfq_id not in pending_rfq_ids:
                    continue

                print(f"\n  Subject : {subject}")
                print(f"  From    : {from_field}")
                print(f"  Msg-ID  : {message_id}")

                # Skip if this exact email was already processed
                if message_id and processed_msg_ids.get(subject_rfq_id) == message_id:
                    print(f"  SKIP — same email already processed (Message-ID matches)")
                    continue

                # Use stored vendor email for DB update
                vendor_email = rfq_to_email[subject_rfq_id]
                print(f"  MATCH -> RFQ-{subject_rfq_id} | vendor: {vendor_email}")

                full_text, raw_body = extract_email_content(msg)
                print(f"  Body: {len(raw_body)} chars")

                saved = save_quote(
                    subject_rfq_id, vendor_email,
                    full_text, raw_body, message_id
                )
                if saved:
                    processed += 1
                    # Update local cache so duplicate emails in same fetch are skipped
                    processed_msg_ids[subject_rfq_id] = message_id

            except Exception as e:
                print(f"  Error: {e}")
                continue

    finally:
        mail.logout()

    print(f"\n======== DONE — {processed} quote(s) updated ========\n")
    return processed