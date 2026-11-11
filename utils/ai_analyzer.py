
import json
from utils.config import get_config
from google import genai


MODEL_NAME = "gemini-3.6-flash"


def analyze_invoice(
    invoice,
    previous_invoices=None,
    arithmetic_result=None,
    duplicate_detected=False
):

    api_key = get_config("GEMINI_API_KEY")

    if not api_key:
        return {
            "available": False,
            "error": "Gemini API key not found."
        }

    try:
        client = genai.Client(api_key=api_key)

        previous_invoices = previous_invoices or []

        history = [
            {
                "vendor": item.get("vendor"),
                "invoice_number": item.get("invoice_number"),
                "amount": item.get("amount")
            }
            for item in previous_invoices[:20]
        ]

        invoice_context = {
            "invoice": invoice,
            "currency": "INR (Indian Rupees), unless explicitly stated otherwise",
            "previous_invoices": history,
            "arithmetic_check": arithmetic_result,
            "duplicate_detected": duplicate_detected
        }

        prompt = f"""
You are a careful invoice risk analysis assistant for InvoiceGuard AI.

Analyze this invoice information:

{json.dumps(invoice_context, indent=2, default=str)}

IMPORTANT CLASSIFICATION RULES:

1. GENUINE RISK INDICATORS:
- A confirmed duplicate invoice.
- An arithmetic mismatch.
- Contradictory invoice details.
- Clearly inconsistent dates or amounts.
- Other specific, evidence-based irregularities.

2. NEUTRAL OBSERVATIONS:
- A first-time vendor.
- An additional delivery or handling charge.
- Missing optional information.
- A normal payment term.
- Any detail that deserves context but is not evidence of wrongdoing.

3. VERIFIED CHECKS:
- Correct arithmetic is a passed check, not a risk.
- No duplicate found is a passed check, not a risk.

SCORING GUIDELINES:
- No confirmed issues: generally 0-20 (Low).
- Minor inconsistencies requiring review: 21-60 (Medium).
- Confirmed duplicate or significant arithmetic mismatch: generally 61-90 (High).
- Multiple serious, evidence-based issues: potentially 91-100 (High).

IMPORTANT:
- A duplicate submission is a risk, but NOT proof of fraud.
- A first-time vendor is NOT automatically suspicious.
- An additional charge is NOT automatically suspicious.
- Never invent details or claim an invoice is definitely fraudulent.
- Do not say an invoice has already been paid unless payment records confirm it.
- Use ₹ for INR amounts. Never convert INR amounts into dollars.
- If information is insufficient, explain that clearly.
- Recommendations must be practical and based on the findings.

Return ONLY valid JSON in this structure:

{{
    "risk_score": 0,
    "summary": "Short explanation",
    "indicators": [
        "Genuine evidence-based risk indicator"
    ],
    "observations": [
        "Neutral observation that may need context"
    ],
    "recommendations": [
        "Suggested action"
    ]
}}

Use empty arrays when there are no findings in a category.
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        result_text = (response.text or "").strip()

        if result_text.startswith("```"):
            result_text = result_text.replace("```json", "")
            result_text = result_text.replace("```", "").strip()

        result = json.loads(result_text)

        score = int(result["risk_score"])

        if not 0 <= score <= 100:
            raise ValueError("Invalid AI risk score.")

        if score <= 30:
            risk_level = "Low"
        elif score <= 60:
            risk_level = "Medium"
        else:
            risk_level = "High"

        return {
            "available": True,
            "risk_score": score,
            "risk_level": risk_level,
            "summary": result["summary"],
            "indicators": result.get("indicators", []),
            "observations": result.get("observations", []),
            "recommendations": result.get("recommendations", [])
        }

    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }