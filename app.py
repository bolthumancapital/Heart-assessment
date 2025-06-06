# app.py (slightly modified to accept JSON payload)

import os, traceback, json
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing environment variable: OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

@app.route("/", methods=["GET"])
def index():
    # Serve our single-page “conversational” HTML
    return app.send_static_file("index.html")

@app.route("/score", methods=["POST"])
def score():
    try:
        data = request.get_json() or {}
        q1_answer = data.get("work_feeling", "").strip()
        q2_answer = data.get("team_feeling", "").strip()
        q3_answer = data.get("leadership_feeling", "").strip()
        q4_answer = data.get("company_people_feeling", "").strip()

        prompt = f"""
You are an employee engagement expert. I will provide four emoji‐based responses from a single respondent:
  1) Work feeling:    "{q1_answer}"
  2) Team feeling:    "{q2_answer}"
  3) Leadership:      "{q3_answer}"
  4) Company people:  "{q4_answer}"

Using the H.E.A.R.T. framework (Happiness, Engagement, Autonomy, Recognition, Trust), please:
  • Give a numeric score (0–10) for each of the five categories:
      - Happiness
      - Engagement
      - Autonomy
      - Recognition
      - Trust
  • Then provide a one-sentence rationale for each score.

Format your answer exactly as:

Happiness: <score>/10 – <brief sentence>
Engagement: <score>/10 – <brief sentence>
Autonomy: <score>/10 – <brief sentence>
Recognition: <score>/10 – <brief sentence>
Trust: <score>/10 – <brief sentence>
"""
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
        return jsonify({ "heart_scores": gpt_reply }), 200

    except Exception as e:
        print("❌ SERVER ERROR:", e)
        traceback.print_exc()
        return jsonify({ "error": str(e) }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
