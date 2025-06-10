# app.py

import io
import sys

# Wrap stdout/stderr in text wrappers with UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import os
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from science_model import run_ctt_analysis_from_raw

app = Flask(__name__)

# ─── Initialize OpenAI client ────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing environment variable: OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
# ────────────────────────────────────────────────────────────────────────────

# ─── Serve static UI ─────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(
        directory=os.path.join(os.path.dirname(__file__), "static"),
        path="index.html"
    )

# ─── Webhook: H.E.A.R.T. + CTT combo ──────────────────────────────────────
@app.route("/formester-webhook", methods=["POST"])
def formester_webhook():
    try:
        incoming = request.get_json(force=True)
print("➡️ Incoming payload:", json.dumps(incoming, indent=2, ensure_ascii=False), flush=True)
...
print("🔬 CTT results:\n", json.dumps(science_ctt, indent=2, ensure_ascii=False), flush=True)

        # H.E.A.R.T. responses
        work_ans   = incoming.get("work_feeling", "").strip()
        team_ans   = incoming.get("team_feeling", "").strip()
        lead_ans   = incoming.get("leadership_feeling", "").strip()
        ppl_ans    = incoming.get("company_people_feeling", "").strip()

        # Build GPT prompt
        prompt = (
            f'You are an employee engagement expert. I will provide four emoji-based responses:\n'
            f'1) Work feeling:    "{work_ans}"\n'
            f'2) Team feeling:    "{team_ans}"\n'
            f'3) Leadership:      "{lead_ans}"\n'
            f'4) Company people:  "{ppl_ans}"\n\n'
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
        print("✏️ Prompt to GPT:\n", prompt)

        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in employee engagement."},
                {"role": "user",   "content": prompt}
            ]
        )
        heart_scores = resp.choices[0].message.content.strip()
        print("✅ GPT reply:\n", heart_scores)

        # CTT analysis
        raw = incoming.get("responses", [])
        science_ctt = run_ctt_analysis_from_raw(raw)
        print("🔬 CTT results:\n", json.dumps(science_ctt, indent=2))

        return jsonify({"heart_scores": heart_scores, "science_ctt": science_ctt}), 200

    except Exception as e:
        print("❌ SERVER ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500

# ─── Main entry ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    # Launch with explicit UTF-8 mode:
    #   python3 -X utf8 app.py
    app.run(host="0.0.0.0", port=port, debug=True)
