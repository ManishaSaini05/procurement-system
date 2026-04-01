import anthropic
import json
import os

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def extract_vendor_quote(email_text):

    prompt = f"""
You are a procurement data extractor.

From the vendor quotation email below extract:

1. unit_price
2. delivery_time
3. payment_terms

Return ONLY valid JSON.

Email:
{email_text}
"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=200,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    text = response.content[0].text

    try:
        data = json.loads(text)
        return data
    except:
        return None