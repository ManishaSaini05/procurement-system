from services.rule_based_extractor import extract_rfq_data

sample_email = """
Dear Team,

We are pleased to quote Rs. 5,200 per unit.
Delivery within 10 days from PO.
Payment terms: 30 days credit.
GST 18% extra.

Regards,
Vendor
"""

result = extract_rfq_data(sample_email)

print("Extraction Result:")
print(result)