# app.py

import os
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from science_model import run_ctt_analysis_from_raw

app = Flask(__name__)

# --- Initialize OpenAI client ------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing environment variable: OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
# ------------------------------------------------------

# --- Serve static UI -------------------------------
@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(
        directory=os.path.join(os.path.dirname(__file__), "static"),
        path="index.html"
    )

# --- Webhook: H.E.A.R.T. + CTT combo -----------------
@app.route("/formester-webhook", methods=["POST"])
def formester_webhook():
    try:
        incoming = request.get_json(force=True)

        # 1) H.E.A.R.T. inputs
        work_ans   = incoming.get("work_feeling", "")
        team_ans   = incoming.get("team_feeling", "")
        lead_ans   = incoming.get("leadership_feeling", "")
        ppl_ans    = incoming.get("company_people_feeling", "")

        # 2) Build GPT prompt
        prompt = (
            f"You are an employee engagement expert. I will provide four emoji-based responses:\n"
            f"1) Work:    \"{work_ans}\"\n"
            f"2) Team:    \"{team_ans}\"\n"
            f"3) Lead:    \"{lead_ans}\"\n"
            f"4) People:  \"{ppl_ans}\"\n\n"
            "Using the H.E.A.R.T. framework (Happiness, Engagement, Autonomy, Recognition, Trust), please:\n"
            "  • Give a numeric score (0-10) for each category\n"
            "  • Provide a one-sentence rationale for each.\n\n"
            "Format exactly as:\n"
            "Happiness: <score>/10 - <sentence>\n"
            "Engagement: <score>/10 - <sentence>\n"
            "Autonomy: <score>/10 - <sentence>\n"
            "Recognition: <score>/10 - <sentence>\n"
            "Trust: <score>/10 - <sentence>"
        )

        # 3) Call GPT for H.E.A.R.T.
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in employee engagement."},
                {"role": "user",   "content": prompt}
            ]
        )
        heart_scores = resp.choices[0].message.content.strip()

        # 4) Run CTT analysis on SPARK responses
        raw = incoming.get("responses", [])
        science_ctt = run_ctt_analysis_from_raw(raw)

        # 5) Return combined results
        return jsonify({
            "heart_scores": heart_scores,
            "science_ctt":  science_ctt
        }), 200

    except Exception as e:
        # Log full traceback to server logs
        traceback.print_exc()
        # Return error details (no printing to console)
        return jsonify({
            "error":   "Server error",
            "details": str(e)
        }), 500

# --- Main entry -------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
