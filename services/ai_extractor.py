# import os
# import json
# from anthropic import Anthropic
# from dotenv import load_dotenv

# # Load .env file
# load_dotenv()

# api_key = os.getenv("ANTHROPIC_API_KEY")

# client = Anthropic(api_key=api_key)
# print("Claude API Loaded:", api_key[:10])
#correct

# print("AI EXTRACTOR FILE LOADED")

# import json
# import re
# from anthropic import Anthropic

# # =====================================
# # CLAUDE API KEY
# # =====================================

# API_KEY = "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"

# client = Anthropic(api_key=API_KEY)

# print("Claude API Loaded:", API_KEY[:12])


# # =====================================
# # EXTRACT VENDOR QUOTE
# # =====================================

# def extract_vendor_quote(email_text):

# #     prompt = f"""
# # You are reading a vendor quotation email.

# # Extract the following information.

# # unit_price
# # delivery_days
# # payment_terms

# # Return ONLY JSON.

# # Example:

# # {{
# # "unit_price": "",
# # "delivery_days": "",
# # "payment_terms": ""
# # }}

# # Email:
# # {email_text}
# # """
#     prompt = f"""
# You are an AI that extracts quotation data from vendor emails.

# Extract these fields from the email.

# Return JSON only.

# Fields:
# - unit_price
# - delivery_days
# - payment_terms

# Rules:
# - unit_price = numeric value only (example: 5000)
# - delivery_days = delivery time (example: 4 weeks, 25 days, immediate)
# - payment_terms = credit or advance terms (example: 30 days credit)

# The email may use different wording like:
# price, quote, rate, lead time, delivery schedule, payment etc.

# Email:
# {email_text}
# """

#     try:

#         response = client.messages.create(
#             model="claude-haiku-4-5-20251001",
#             max_tokens=200,
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )

#         text = response.content[0].text

#         json_match = re.search(r"\{.*\}", text, re.DOTALL)

#         if json_match:
#             return json.loads(json_match.group())

#         return {}

#     except Exception as e:

#         print("Claude extraction failed:", e)
#         return {}

print("AI EXTRACTOR FILE LOADED")

import json
import re
import os
from anthropic import Anthropic

# =====================================
# CLAUDE CLIENT — key from environment
# Never hardcode API keys in source code!
# Set ANTHROPIC_API_KEY in your .env or st.secrets
# =====================================

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# =====================================
# EXTRACT VENDOR QUOTE
# =====================================

def extract_vendor_quote(email_text):

    prompt = f"""
You are an AI that extracts quotation data from vendor emails.

Extract these fields from the email and return JSON only.

Fields:
- unit_price: numeric value only (example: 5000)
- delivery_days: delivery time string (example: "4 weeks", "25 days", "immediate")
- payment_terms: credit or advance terms (example: "30 days credit", "50% advance")

The email may use different wording like:
price, quote, rate, lead time, delivery schedule, payment etc.

Return ONLY valid JSON with no extra text.

Email:
{email_text}
"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        text = response.content[0].text.strip()

        # Strip markdown code fences if present
        text = re.sub(r"```json|```", "", text).strip()

        json_match = re.search(r"\{.*\}", text, re.DOTALL)

        if json_match:
            return json.loads(json_match.group())

        return {}

    except Exception as e:
        print("Claude extraction failed:", e)
        return {}