# app.py

import sys
import os
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from science_model import run_ctt_analysis_from_raw

# ─── Force UTF-8 for all stdout/stderr ───────────────────────────────────
# (so print() won’t crash on emojis or “…”)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

app = Flask(__name__)

# ─── Initialize OpenAI client ────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing environment variable: OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
# ────────────────────────────────────────────────────────────────────────────

# ─── Serve the static UI ──────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(
        directory=os.path.join(os.path.dirname(__file__), "static"),
        path="index.html"
    )

# ─── Webhook: H.E.A.R.T. + CTT combo ───────────────────────────────────────
@app.route("/formester-webhook", methods=["POST"])
def formester_webhook():
    try:
        incoming = request.get_json(force=True)
        print("➡️ Incoming payload:", json.dumps(incoming, indent=2), flush=True)

        # 1) H.E.A.R.T. inputs
        work_ans   = incoming.get("work_feeling", "").strip()
        team_ans   = incoming.get("team_feeling", "").strip()
        lead_ans   = incoming.get("leadership_feeling", "").strip()
        people_ans = incoming.get("company_people_feeling", "").strip()

        # 2) Build and send prompt to GPT
        prompt = f"""
You are an employee engagement expert. I will provide four emoji-based responses:
1) Work feeling:    "{work_ans}"
2) Team feeling:    "{team_ans}"
3) Leadership:      "{lead_ans}"
4) Company people:  "{people_ans}"

Using the H.E.A.R.T. framework (Happiness, Engagement, Autonomy, Recognition, Trust), please:
  • Give a numeric score (0-10) for each category
  • Provide a one-sentence rationale for each.

Format exactly as:
Happiness: <score>/10 - <sentence>
Engagement: <score>/10 - <sentence>
Autonomy: <score>/10 - <sentence>
Recognition: <score>/10 - <sentence>
Trust: <score>/10 - <sentence>
"""
        print("✏️ Prompt to GPT:\n", prompt, flush=True)
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",  "content": "You are an expert in employee engagement."},
                {"role": "user",    "content": prompt}
            ]
        )
        heart_scores = resp.choices[0].message.content.strip()
        print("✅ GPT reply:\n", heart_scores, flush=True)

        # 3) CTT-based analysis on your 15 SPARK answers
        raw = incoming.get("responses", [])
        science_ctt = run_ctt_analysis_from_raw(raw)
        print("🔬 CTT results:\n", json.dumps(science_ctt, indent=2), flush=True)

        # 4) Combined response
        return jsonify({
            "heart_scores": heart_scores,
            "science_ctt":  science_ctt
        }), 200

    except Exception as e:
        print("❌ SERVER ERROR:", e, flush=True)
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500

# ─── Main entry ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Use the PORT env var if available (Render sets this), otherwise 10000
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
