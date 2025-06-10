# app.py

import os
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from science_model import run_ctt_analysis_from_raw

app = Flask(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing environment variable: OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Serve static UI
@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(
        directory=os.path.join(os.path.dirname(__file__), "static"),
        path="index.html"
    )

# Webhook endpoint
@app.route("/formester-webhook", methods=["POST"])
def formester_webhook():
    try:
        data = request.get_json(force=True)

        # Gather emoji answers (they may contain unicode)
        work_ans   = data.get("work_feeling", "")
        team_ans   = data.get("team_feeling", "")
        lead_ans   = data.get("leadership_feeling", "")
        people_ans = data.get("company_people_feeling", "")

        # Plain-ASCII prompt template
        prompt = (
            "You are an employee engagement expert. I will provide four emoji-based responses:\n"
            f"1) Work feeling:    \"{work_ans}\"\n"
            f"2) Team feeling:    \"{team_ans}\"\n"
            f"3) Leadership:      \"{lead_ans}\"\n"
            f"4) Company people:  \"{people_ans}\"\n\n"
            "Using the H.E.A.R.T. framework, please:\n"
            "  - Give a numeric score (0-10) for each category: Happiness, Engagement, "
            "Autonomy, Recognition, Trust\n"
            "  - Provide a one-sentence rationale for each score.\n\n"
            "Format exactly as:\n"
            "Happiness: <score>/10 - <sentence>\n"
            "Engagement: <score>/10 - <sentence>\n"
            "Autonomy: <score>/10 - <sentence>\n"
            "Recognition: <score>/10 - <sentence>\n"
            "Trust: <score>/10 - <sentence>"
        )

        # Call GPT
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in employee engagement."},
                {"role": "user",   "content": prompt}
            ]
        )
        heart_scores = resp.choices[0].message.content.strip()

        # Run CTT analysis
        raw = data.get("responses", [])
        science_ctt = run_ctt_analysis_from_raw(raw)

        # Return combined results
        return jsonify({
            "heart_scores": heart_scores,
            "science_ctt":  science_ctt
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error":   "Server error",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
