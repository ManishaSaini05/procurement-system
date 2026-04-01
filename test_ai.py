from services.ai_extractor import extract_quote

email = """
Hello,

We can supply modules at ₹4,850 per unit.

Delivery: 3 weeks
Payment: 30 days credit

Regards
ABC Solar
"""

result = extract_quote(email)

print(result)