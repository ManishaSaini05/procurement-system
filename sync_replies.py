from services.gmail_service import fetch_rfq_replies

print("Checking mailbox for RFQ replies...")

fetch_rfq_replies()

print("Finished checking emails.")