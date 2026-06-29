from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ==========================
# ✅ WEEKLY PLAN (EXISTING)
# ==========================
def generate_weekly_plan(data, prediction, risk):
    prompt = f"""
Patient Details:
Age: {data.age}
BP: {data.trestbps}
Cholesterol: {data.chol}
Risk Level: {risk}%

Prediction: {prediction}

Generate a weekly routine in STRICT JSON format like this:

{{
  "Monday": {{
    "diet": "...",
    "exercise": "...",
    "precautions": "..."
  }},
  "Tuesday": {{
    "diet": "...",
    "exercise": "...",
    "precautions": "..."
  }},
  "Wednesday": {{
    "diet": "...",
    "exercise": "...",
    "precautions": "..."
  }},
  "Thursday": {{
    "diet": "...",
    "exercise": "...",
    "precautions": "..."
  }},
  "Friday": {{
    "diet": "...",
    "exercise": "...",
    "precautions": "..."
  }},
  "Saturday": {{
    "diet": "...",
    "exercise": "...",
    "precautions": "..."
  }},
  "Sunday": {{
    "diet": "...",
    "exercise": "...",
    "precautions": "..."
  }}
}}

IMPORTANT:
- Return ONLY JSON
- No explanation
- No markdown
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.choices[0].message.content

    # Clean unwanted formatting
    response_text = response_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(response_text)
    except Exception:
        return {
            "error": "Failed to parse AI response",
            "raw_text": response_text
        }


# ==========================
# 🧠 NEW FEATURE: INTERPRETATION
# ==========================
def generate_interpretation(data, prediction, risk):
    prompt = f"""
You are a cardiology assistant.

Analyze the patient data and provide a short clinical interpretation.

Patient Details:
Age: {data.age}
BP: {data.trestbps}
Cholesterol: {data.chol}
Max Heart Rate: {data.thalach}
Exercise Angina: {data.exang}
Risk Level: {risk}%

Prediction: {prediction}

Rules:
- Keep it short (2-3 lines)
- Professional medical tone
- Do NOT give final diagnosis
- Give advisory only
- No markdown, no extra formatting
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    interpretation = response.choices[0].message.content.strip()

    return interpretation