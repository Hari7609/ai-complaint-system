import os
import json
import re

try:
    from google import genai
except ImportError:
    genai = None


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


# ============================================================
# FALLBACK AI
# ============================================================

def fallback_analysis(text, selected_category="General"):
    text_lower = text.lower()

    # Category detection
    if any(word in text_lower for word in [
        "hack", "hacked", "password", "phishing", "fraud",
        "scam", "security", "unauthorized", "account stolen"
    ]):
        category = "Security"

    elif any(word in text_lower for word in [
        "payment", "money", "refund", "invoice", "billing",
        "transaction", "charged", "fee"
    ]):
        category = "Billing"

    elif any(word in text_lower for word in [
        "error", "bug", "crash", "login", "website",
        "application", "server", "network", "technical"
    ]):
        category = "Technical"

    elif selected_category and selected_category != "General":
        category = selected_category

    else:
        category = "General"

    # Priority detection
    if any(word in text_lower for word in [
        "urgent", "emergency", "critical", "immediately",
        "hacked", "fraud", "stolen", "danger"
    ]):
        priority = "Critical"

    elif any(word in text_lower for word in [
        "problem", "issue", "failed", "unable",
        "error", "delay", "not working"
    ]):
        priority = "Medium"

    else:
        priority = "Light"

    # Sentiment
    if any(word in text_lower for word in [
        "angry", "worst", "terrible", "fraud",
        "problem", "failed", "hacked", "bad"
    ]):
        sentiment = "Negative"

    elif any(word in text_lower for word in [
        "thank", "thanks", "good", "great"
    ]):
        sentiment = "Positive"

    else:
        sentiment = "Neutral"

    # Word-based solution
    solutions = {
        "Security":
            "Secure the affected account, change credentials, preserve relevant evidence, "
            "check unauthorized activity, and escalate the incident to the security team.",

        "Billing":
            "Verify the transaction and billing records, identify the disputed amount, "
            "correct the billing issue, and initiate a refund if applicable.",

        "Technical":
            "Reproduce the reported issue, check application and server logs, "
            "identify the root cause, apply the required fix, and verify the service.",

        "General":
            "Review the complaint details, identify the responsible department, "
            "take the appropriate corrective action, and provide the user with an update."
    }

    return {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "summary": solutions.get(category, solutions["General"])
    }


# ============================================================
# GEMINI ANALYSIS
# ============================================================

def analyze_complaint(text, selected_category="General"):

    if not GEMINI_API_KEY or genai is None:
        return fallback_analysis(text, selected_category)

    try:

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""
You are an AI complaint management assistant.

Analyze the following complaint.

Complaint:
{text}

User selected category:
{selected_category}

Return ONLY valid JSON.

Required JSON format:

{{
    "category": "General",
    "priority": "Light",
    "sentiment": "Neutral",
    "summary": "Short practical word-based solution"
}}

Rules:

category must be one of:
General, Billing, Technical, Security

priority must be one of:
Light, Medium, Critical

sentiment must be one of:
Positive, Neutral, Negative

The summary must provide a practical word-based solution/action.
Do not use Markdown.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        result_text = response.text.strip()

        # Remove code fences if Gemini returns them
        result_text = re.sub(
            r"```json\s*|\s*```",
            "",
            result_text,
            flags=re.IGNORECASE
        ).strip()

        result = json.loads(result_text)

        category = result.get("category", "General")
        priority = result.get("priority", "Medium")
        sentiment = result.get("sentiment", "Neutral")
        summary = result.get("summary", "")

        if category not in [
            "General",
            "Billing",
            "Technical",
            "Security"
        ]:
            category = "General"

        if priority not in [
            "Light",
            "Medium",
            "Critical"
        ]:
            priority = "Medium"

        if sentiment not in [
            "Positive",
            "Neutral",
            "Negative"
        ]:
            sentiment = "Neutral"

        return {
            "category": category,
            "priority": priority,
            "sentiment": sentiment,
            "summary": summary
        }

    except Exception as e:

        print("Gemini AI error:", e)

        return fallback_analysis(
            text,
            selected_category
        )