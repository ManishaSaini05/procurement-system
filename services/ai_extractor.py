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

# print("AI EXTRACTOR FILE LOADED")

# import json
# import re
# import os
# from anthropic import Anthropic

# # =====================================
# # CLAUDE CLIENT — key from environment
# # Never hardcode API keys in source code!
# # Set ANTHROPIC_API_KEY in your .env or st.secrets
# # =====================================

# client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# # =====================================
# # EXTRACT VENDOR QUOTE
# # =====================================

# def extract_vendor_quote(email_text):

#     prompt = f"""
# You are an AI that extracts quotation data from vendor emails.

# Extract these fields from the email and return JSON only.

# Fields:
# - unit_price: numeric value only (example: 5000)
# - delivery_days: delivery time string (example: "4 weeks", "25 days", "immediate")
# - payment_terms: credit or advance terms (example: "30 days credit", "50% advance")

# The email may use different wording like:
# price, quote, rate, lead time, delivery schedule, payment etc.

# Return ONLY valid JSON with no extra text.

# Email:
# {email_text}
# """

#     try:
#         response = client.messages.create(
#             model="claude-haiku-4-5-20251001",
#             max_tokens=300,
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )

#         text = response.content[0].text.strip()

#         # Strip markdown code fences if present
#         text = re.sub(r"```json|```", "", text).strip()

#         json_match = re.search(r"\{.*\}", text, re.DOTALL)

#         if json_match:
#             return json.loads(json_match.group())

#         return {}

#     except Exception as e:
#         print("Claude extraction failed:", e)
#         return {}

# import json
# import re
# import os
# from anthropic import Anthropic

# client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# def extract_vendor_quote(text):
#     """
#     Extract unit_price, delivery_days, payment_terms from
#     vendor email body and/or PDF quotation text.
#     """

#     prompt = f"""
# You are a procurement assistant extracting data from a vendor quotation.
# The text below may come from an email body, a PDF quotation, or both.

# Extract ONLY these 3 fields:

# 1. unit_price
#    - Look for: Unit Price, Rate, Price Per Unit, Per Piece, Per Nos
#    - Extract the PER UNIT price only (not total price, not grand total)
#    - Return numeric value only, no currency symbol
#    - Example: 4200

# 2. delivery_days
#    - Look for: Delivery, Lead Time, Delivery Period, Dispatch
#    - Return as a string
#    - Example: "21 days from receipt of PO", "4 weeks", "immediate"

# 3. payment_terms
#    - Look for: Payment Terms, Payment Conditions
#    - Return as a string
#    - Example: "100% payment against Proforma Invoice", "30 days credit"

# Rules:
# - Return ONLY valid JSON, no extra text, no markdown
# - If a field is not found return null
# - Do NOT return total price or grand total as unit_price
# - The unit price is typically in the "Unit Price" column of a table

# Example output:
# {{
#     "unit_price": 4200,
#     "delivery_days": "21 days from receipt of PO",
#     "payment_terms": "100% payment against Proforma Invoice"
# }}

# Quotation Text:
# {text}
# """

#     try:
#         response = client.messages.create(
#             model="claude-haiku-4-5-20251001",
#             max_tokens=300,
#             messages=[{"role": "user", "content": prompt}]
#         )

#         text_response = response.content[0].text.strip()

#         # Strip markdown fences if present
#         text_response = re.sub(r"```json|```", "", text_response).strip()

#         json_match = re.search(r"\{.*\}", text_response, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())

#         return {}

#     except Exception as e:
#         print("Claude extraction failed:", e)
#         return {}

# import json
# import re
# import os
# from anthropic import Anthropic

# client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# def extract_vendor_quote(text):

#     # =============================================
#     # STEP 1: REGEX EXTRACTION (fast, reliable)
#     # Works directly on the structured PDF text
#     # =============================================

#     unit_price    = None
#     delivery_days = None
#     payment_terms = None

#     # --- UNIT PRICE ---
#     # Match "Unit Price | 4200" or "Unit Price 4200" pattern from table
#     # Specifically looks for Unit Price column followed by the value
#     # Avoids Total Price, Grand Total, GST amounts
#     price_match = re.search(
#         r'Nos\s*[|]?\s*(\d{3,7})\s*[|]?\s*\d{6,}',  # Nos | 4200 | 63000000
#         text
#     )
#     if not price_match:
#         price_match = re.search(
#             r'Unit\s*Price\s*[|\s]+(\d{3,7})\b',      # Unit Price | 4200
#             text, re.IGNORECASE
#         )
#     if not price_match:
#         # Last resort: find price between unit column and a much larger total
#         price_match = re.search(
#             r'\bNos\b[^\d]*(\d{3,6})\b',              # after "Nos"
#             text, re.IGNORECASE
#         )
#     if price_match:
#         unit_price = float(price_match.group(1))

#     # --- DELIVERY ---
#     # Match "Delivery | 21 days from the receipt of PO"
#     delivery_match = re.search(
#         r'Delivery\s*[|\:]\s*([^\n|]+)',
#         text, re.IGNORECASE
#     )
#     if delivery_match:
#         delivery_days = delivery_match.group(1).strip()

#     # --- PAYMENT TERMS ---
#     # Match "Payment Terms | 100% payment against Proforma Invoice"
#     payment_match = re.search(
#         r'Payment\s*Terms?\s*[|\:]\s*([^\n|]+)',
#         text, re.IGNORECASE
#     )
#     if payment_match:
#         payment_terms = payment_match.group(1).strip()

#     # If all 3 found by regex, return immediately — no need for AI
#     if unit_price and delivery_days and payment_terms:
#         print(f"✅ Regex extracted — Price: {unit_price} | Delivery: {delivery_days} | Payment: {payment_terms}")
#         return {
#             "unit_price": unit_price,
#             "delivery_days": delivery_days,
#             "payment_terms": payment_terms
#         }

#     # =============================================
#     # STEP 2: AI EXTRACTION (fallback)
#     # Only runs if regex missed something
#     # =============================================

#     print("Regex incomplete — trying AI extraction...")

#     prompt = f"""
# You are extracting data from a vendor quotation document.

# The document has a table with these columns:
# Sl No | Material | Product Description | QTY | Unit | Unit Price | Total Price

# And a terms section like:
# Payment Terms | 100% payment against Proforma Invoice  
# Delivery | 21 days from the receipt of PO

# Extract exactly these 3 fields and return ONLY valid JSON:

# {{
#     "unit_price": <number from Unit Price column, NOT Total Price or Grand Total>,
#     "delivery_days": "<full delivery string>",
#     "payment_terms": "<full payment terms string>"
# }}

# Rules:
# - unit_price is the small per-unit number (like 4200), NOT the large total (like 63000000)
# - If not found return null for that field
# - Return JSON only, no markdown, no explanation

# Already extracted by regex (null means not found yet):
# unit_price: {unit_price}
# delivery_days: {delivery_days}
# payment_terms: {payment_terms}

# Document:
# {text[:3000]}
# """

#     try:
#         response = client.messages.create(
#             model="claude-haiku-4-5-20251001",
#             max_tokens=300,
#             messages=[{"role": "user", "content": prompt}]
#         )

#         text_response = response.content[0].text.strip()
#         text_response = re.sub(r"```json|```", "", text_response).strip()

#         json_match = re.search(r"\{.*\}", text_response, re.DOTALL)
#         if json_match:
#             ai_data = json.loads(json_match.group())

#             # Only fill in what regex missed
#             if not unit_price and ai_data.get("unit_price"):
#                 unit_price = float(ai_data["unit_price"])
#             if not delivery_days and ai_data.get("delivery_days"):
#                 delivery_days = ai_data["delivery_days"]
#             if not payment_terms and ai_data.get("payment_terms"):
#                 payment_terms = ai_data["payment_terms"]

#     except Exception as e:
#         print(f"AI extraction failed: {e}")

#     return {
#         "unit_price": unit_price,
#         "delivery_days": delivery_days,
#         "payment_terms": payment_terms
#     }

# New version #

import json
import re
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def extract_vendor_quote(text):
    """
    Extract unit_price, delivery_days, payment_terms
    from vendor email body and/or PDF quotation text.
    Uses regex first (fast), falls back to AI.
    """

    unit_price    = None
    delivery_days = None
    payment_terms = None

    # --- UNIT PRICE ---
    # Pattern 1: "Nos | 4200 | 63000000" — value between unit and large total
    m = re.search(r'Nos\s*[|]?\s*(\d{3,7})\s*[|]?\s*\d{6,}', text)
    if not m:
        # Pattern 2: "Unit Price | 4200"
        m = re.search(r'Unit\s*Price\s*[|\s]+(\d{3,7})\b', text, re.IGNORECASE)
    if not m:
        # Pattern 3: value after "Nos" keyword
        m = re.search(r'\bNos\b[^\d]*(\d{3,6})\b', text, re.IGNORECASE)
    if m:
        unit_price = float(m.group(1))

    # --- DELIVERY ---
    # Pattern: "Delivery | 21 days from the receipt of PO"
    m = re.search(r'Delivery\s*[|:]\s*([^\n|]+)', text, re.IGNORECASE)
    if m:
        delivery_days = m.group(1).strip()
    if not delivery_days:
        m = re.search(r'(\d+)\s*(day|days|week|weeks)[^\n]*', text, re.IGNORECASE)
        if m:
            delivery_days = m.group(0).strip()

    # --- PAYMENT TERMS ---
    # Pattern: "Payment Terms | 100% payment against Proforma Invoice"
    m = re.search(r'Payment\s*Terms?\s*[|:]\s*([^\n|]+)', text, re.IGNORECASE)
    if m:
        payment_terms = m.group(1).strip()
    if not payment_terms:
        m = re.search(r'(advance|credit|payment\s*\d+\s*days)', text, re.IGNORECASE)
        if m:
            payment_terms = m.group(0).strip()

    # If all found, return without calling AI
    if unit_price and delivery_days and payment_terms:
        print(f"Regex extracted — Price:{unit_price} | Delivery:{delivery_days} | Payment:{payment_terms}")
        return {"unit_price": unit_price, "delivery_days": delivery_days, "payment_terms": payment_terms}

    # --- AI FALLBACK ---
    print("Regex incomplete, using AI extraction...")
    try:
        prompt = f"""
You are extracting data from a vendor quotation (email or PDF).

The document has a table:
Sl No | Material | Product Description | QTY | Unit | Unit Price | Total Price

And a terms section:
Payment Terms | ...
Delivery | ...

Extract exactly these 3 fields. Return ONLY valid JSON:
{{
    "unit_price": <number, NOT Total Price or Grand Total>,
    "delivery_days": "<full delivery string or null>",
    "payment_terms": "<full payment terms or null>"
}}

Already found by regex (null = not found yet):
unit_price: {unit_price}
delivery_days: {delivery_days}
payment_terms: {payment_terms}

Document (first 3000 chars):
{text[:3000]}
"""
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            ai = json.loads(match.group())
            if not unit_price and ai.get("unit_price"):
                unit_price = float(ai["unit_price"])
            if not delivery_days and ai.get("delivery_days"):
                delivery_days = ai["delivery_days"]
            if not payment_terms and ai.get("payment_terms"):
                payment_terms = ai["payment_terms"]
    except Exception as e:
        print(f"AI extraction failed: {e}")

    return {"unit_price": unit_price, "delivery_days": delivery_days, "payment_terms": payment_terms}