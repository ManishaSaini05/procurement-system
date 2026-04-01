from services.gmail_service import extract_rfq_data

emails = extract_rfq_data()

print("Emails Found:")
for e in emails:
    print(e["subject"])
    print(e["from"])
    print("------")