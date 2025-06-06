# app.py

import os
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__)

# ─── 1) Initialize OpenAI client ──────────────────────────────────────────
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing environment variable: OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
# ────────────────────────────────────────────────────────────────────────────


# ─── 2) Serve index.html from the "static" folder ────────────────────────
@app.route("/", methods=["GET"])
def serve_index():
    """
    When someone visits the root URL, send them the static/index.html file.
    All of our chat UI lives in that file.
    """
    # __file__ refers to this app.py; we want the sibling "static/index.html"
    return send_from_directory(
        directory=os.path.join(os.path.dirname(__file__), "static"),
        path="index.html"
    )


# ─── 3) The Formester webhook endpoint ────────────────────────────────────
@app.route("/formester-webhook", methods=["POST"])
def formester_webhook():
    """
    This endpoint is called when the front-end (script.js) POSTs the four emoji answers.
    We extract them, call OpenAI, and return a JSON with "heart_scores".
    """
    try:
        incoming = request.json
        print("➡️ Incoming payload:", json.dumps(incoming, indent=2))

        # Extract the four answers (keys match your JavaScript "answers" object)
        # Each will be a single emoji+label string, e.g. "😀 Energized"
        work_answer    = incoming.get("work_feeling", "").strip()
        team_answer    = incoming.get("team_feeling", "").strip()
        lead_answer    = incoming.get("leadership_feeling", "").strip()
        people_answer  = incoming.get("company_people_feeling", "").strip()

        print("📝 Extracted answers:", work_answer, team_answer, lead_answer, people_answer)

        # If any are missing, warn (optional)
        missing = [
            lbl for lbl, ans in [
                ("work_feeling", work_answer),
                ("team_feeling", team_answer),
                ("leadership_feeling", lead_answer),
                ("company_people_feeling", people_answer)
            ] if ans == ""
        ]
        if missing:
            print("⚠️ WARNING: Missing answers for:", missing)

        # Build the GPT prompt
        prompt = f"""
You are an employee engagement expert. I will provide four emoji‐based responses:
1) Work feeling:    "{work_answer}"
2) Team feeling:    "{team_answer}"
3) Leadership:      "{lead_answer}"
4) Company people:  "{people_answer}"

Using the H.E.A.R.T. framework (Happiness, Engagement, Autonomy, Recognition, Trust), please:
  • Give a numeric score (0–10) for each of the five categories:
      - Happiness
      - Engagement
      - Autonomy
      - Recognition
      - Trust
  • Then provide a one‐sentence rationale for each score.

Format your answer exactly as:

Happiness: <score>/10 – <brief sentence>
Engagement: <score>/10 – <brief sentence>
Autonomy: <score>/10 – <brief sentence>
Recognition: <score>/10 – <brief sentence>
Trust: <score>/10 – <brief sentence>
"""
        print("✏️  Composed prompt:\n", prompt)

        # Call GPT-3.5-turbo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in employee engagement, especially the H.E.A.R.T. model."
                },
                { "role": "user", "content": prompt }
            ]
        )

        heart_scores = response.choices[0].message.content.strip()
        print("✅ GPT reply:\n", heart_scores)

        # Return JSON containing "heart_scores"
        return jsonify({ "heart_scores": heart_scores }), 200

    except Exception as e:
        print("❌ SERVER ERROR:", e)
        traceback.print_exc()
        return jsonify({ "error": "Server error", "details": str(e) }), 500


# ─── 4) Main entry point ───────────────────────────────────────────────────
if __name__ == "__main__":
    # Locally, Flask will listen on port 10000
    app.run(host="0.0.0.0", port=10000)
