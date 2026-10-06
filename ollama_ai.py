import json
import ollama

MODEL = "llama3.2:latest"


def analyze_complaint(complaint):
    prompt = f"""
You are an AI customer complaint analyzer.

Analyze this customer complaint:

{complaint}

Return a JSON object with exactly these fields:

{{
    "category": "Billing",
    "sentiment": "Negative",
    "priority": "High",
    "summary": "Short summary",
    "key_issues": ["Issue 1", "Issue 2"],
    "root_cause": "Possible root cause",
    "feedback": "Useful feedback for the company",
    "suggested_action": "Recommended action for support team",
    "suggested_response": "Professional response to the customer"
}}

Rules:
- category must be one of:
  Product, Service, Billing, Delivery, Technical, Account, Refund, Other
- sentiment must be one of:
  Positive, Neutral, Negative
- priority must be one of:
  Low, Medium, High, Critical
- key_issues must be a JSON list
- Return JSON only
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json",
        options={
            "temperature": 0
        }
    )

    content = response["message"]["content"].strip()

    try:
        result = json.loads(content)

        return {
            "category": result.get("category", "Other"),
            "sentiment": result.get("sentiment", "Neutral"),
            "priority": result.get("priority", "Medium"),
            "summary": result.get("summary", ""),
            "key_issues": result.get("key_issues", []),
            "root_cause": result.get("root_cause", ""),
            "feedback": result.get("feedback", ""),
            "suggested_action": result.get("suggested_action", ""),
            "suggested_response": result.get("suggested_response", "")
        }

    except json.JSONDecodeError:
        return {
            "category": "Other",
            "sentiment": "Neutral",
            "priority": "Medium",
            "summary": content,
            "key_issues": [],
            "root_cause": "Unable to determine",
            "feedback": "Please review the complaint manually.",
            "suggested_action": "Assign the complaint to the appropriate support team.",
            "suggested_response": "Thank you for contacting us. We are reviewing your complaint."
        }