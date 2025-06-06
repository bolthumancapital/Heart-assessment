# app.py

import os
import json
import traceback

from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing environment variable: OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

@app.route("/", methods=["GET"])
def index():
    return "👋 Koonman Formester Webhook is LIVE!"

@app.route("/formester-webhook", methods=["POST"])
def formester_webhook():
    try:
        incoming = request.json
        print("➡️ Incoming Formester payload:\n", json.dumps(incoming, indent=2))

        data = incoming
        # For our pure‐UI version, we’re receiving a payload like { work_feeling: "...", ... }
        # Instead of the old Formester format; so just grab the four keys directly:
        q1 = data.get("work_feeling", "").strip()
        q2 = data.get("team_feeling", "").strip()
        q3 = data.get("leadership_feeling", "").strip()
        q4 = data.get("company_people_feeling", "").strip()

        # _(Optional)_ Debug the 4 answers:
        print(f"📝 Extracted Answers:\n  work: {q1}\n  team: {q2}\n  lead: {q3}\n  comp: {q4}")

        prompt = f"""
You are an employee engagement expert. I will provide four emoji‐based responses from a single respondent:
  1) Work feeling:    "{q1}"
  2) Team feeling:    "{q2}"
  3) Leadership:      "{q3}"
  4) Company people:  "{q4}"

Using the H.E.A.R.T. framework (Happiness, Engagement, Autonomy, Recognition, Trust), please:
  • Give a numeric score (0–10) for each of the five categories,
  • Then provide a one‐sentence rationale for each score.

Format your answer exactly as:

Happiness: <score>/10 – <brief sentence>
Engagement: <score>/10 – <brief sentence>
Autonomy: <score>/10 – <brief sentence>
Recognition: <score>/10 – <brief sentence>
Trust: <score>/10 – <brief sentence>
"""
        print("✏️  Composed GPT prompt:\n", prompt)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in employee engagement, especially the H.E.A.R.T. model."
                },
                {"role": "user", "content": prompt}
            ]
        )
        gpt_reply = response.choices[0].message.content.strip()
        print("✅ GPT‐Generated H.E.A.R.T. scores:\n", gpt_reply)

        return jsonify({"response": gpt_reply}), 200

    except Exception as e:
        print("❌ SERVER ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
