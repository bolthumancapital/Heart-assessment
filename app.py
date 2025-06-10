# app.py

import os
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from science_model import run_ctt_analysis_from_raw, QUESTIONS

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
    return send_from_directory(
        directory=os.path.join(os.path.dirname(__file__), "static"),
        path="index.html"
    )


# ─── 3) The Formester webhook endpoint ────────────────────────────────────
@app.route("/formester-webhook", methods=["POST"])
def formester_webhook():
    """
    This endpoint is called when the front-end POSTs the four emoji answers
    PLUS a 'responses' array of your 15 SPARK answers. We call GPT for H.E.A.R.T.
    scores and then run the CTT pipeline.
    """
    try:
        incoming = request.get_json(force=True)
        print("➡️ Incoming payload:", json.dumps(incoming, indent=2))

        # Extract the four legacy H.E.A.R.T. answers
        work_answer   = incoming.get("work_feeling", "").strip()
        team_answer   = incoming.get("team_feeling", "").strip()
        lead_answer   = incoming.get("leadership_feeling", "").strip()
        people_answer = incoming.get("company_people_feeling", "").strip()
        print("📝 Extracted answers:", work_answer, team_answer, lead_answer, people_answer)

        # Build the GPT prompt for H.E.A.R.T. scoring
        prompt = f"""
You are an employee engagement expert. I will provide four emoji‐based responses:
1) Work feeling:    "{work_answer}"
2) Team feeling:    "{team_answer}"
3) Leadership:      "{lead_answer}"
4) Company people:  "{people_answer}"

Using the H.E.A.R.T. framework (Happiness, Engagement, Autonomy, Recognition, Trust), please:
  • Give a numeric score (0–10) for each category
  • Provide a one‐sentence rationale for each.

Format exactly as:
Happiness: <score>/10 – <sentence>
Engagement: <score>/10 – <sentence>
Autonomy: <score>/10 – <sentence>
Recognition: <score>/10 – <sentence>
Trust: <score>/10 – <sentence>
"""
        print("✏️ Composed prompt:\n", prompt)

        # Call GPT for H.E.A.R.T. scores
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in employee engagement."},
                {"role": "user",   "content": prompt}
            ]
        )
        heart_scores = response.choices[0].message.content.strip()
        print("✅ GPT reply:\n", heart_scores)

        # Now run the CTT pipeline on your 15 SPARK responses
        raw_responses = incoming.get("responses", [])
        science_ctt   = run_ctt_analysis_from_raw(raw_responses)
        print("🔬 CTT results:\n", json.dumps(science_ctt, indent=2))

        # Return both
        return jsonify({
            "heart_scores": heart_scores,
            "science_ctt":  science_ctt
        }), 200

    except Exception as e:
        print("❌ SERVER ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500


# ─── 4) Main entry point ───────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)), debug=True)
