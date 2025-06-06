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
        # 1) Read the raw JSON that the client POSTed
        incoming = request.json
        print("➡️ Incoming JSON:\n", json.dumps(incoming, indent=2))

        # 2) Attempt to pull out a Formester‐style payload:
        data = incoming.get("data", {})
        submission = data.get("submission", None)

        # 3) If we didn’t get a Formester “submission”, assume it's our conversational UI:
        if submission is None:
            # Build a “submission” dict with the exact question labels as keys
            submission = {}
            # These are the label‐strings your Flask code was expecting. They must match exactly:
            q1_label = "How does your work feel right now?"
            q2_label = "How do you feel about your team?"
            q3_label = "How do you feel about leadership?"
            q4_label = "Which emoji best captures how you feel about people at your company?"

            # Grab from the flat JSON keys of your UI:
            submission[q1_label] = incoming.get("work_feeling", "").strip()
            submission[q2_label] = incoming.get("team_feeling", "").strip()
            submission[q3_label] = incoming.get("leadership_feeling", "").strip()
            submission[q4_label] = incoming.get("company_people_feeling", "").strip()
        else:
            # If it *is* a Formester payload, re‐define the labels for later use:
            q1_label = "How does your work feel right now?"
            q2_label = "How do you feel about your team?"
            q3_label = "How do you feel about leadership?"
            q4_label = "Which emoji best captures how you feel about people at your company?"

        # 4) Now at this point, `submission` is guaranteed to be a dict of question→answer.
        #    Let’s extract each answer (handling lists as before):
        def extract_answer(label):
            raw = submission.get(label, "")
            if isinstance(raw, list) and len(raw) > 0:
                return str(raw[0]).strip()
            return str(raw).strip()

        q1_answer = extract_answer(q1_label)
        q2_answer = extract_answer(q2_label)
        q3_answer = extract_answer(q3_label)
        q4_answer = extract_answer(q4_label)

        print("📝 Extracted Answers:")
        print(f"    {q1_label} → {q1_answer}")
        print(f"    {q2_label} → {q2_answer}")
        print(f"    {q3_label} → {q3_answer}")
        print(f"    {q4_label} → {q4_answer}")

        # 5) Warn if any are empty
        missing = [
            lbl for lbl, ans in [
                (q1_label, q1_answer),
                (q2_label, q2_answer),
                (q3_label, q3_answer),
                (q4_label, q4_answer)
            ] if ans == ""
        ]
        if missing:
            print("⚠️ WARNING: These questions were blank or missing:", missing)

        # 6) Build the GPT prompt (same as before)
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
  • Then provide a one‐sentence rationale for each score.

Format your answer exactly as:

Happiness: <score>/10 – <brief sentence>
Engagement: <score>/10 – <brief sentence>
Autonomy: <score>/10 – <brief sentence>
Recognition: <score>/10 – <brief sentence>
Trust: <score>/10 – <brief sentence>
"""
        print("✏️  Composed GPT prompt:\n", prompt)

        # 7) Call ChatGPT
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

        # 8) Return JSON with key “heart_scores”
        return jsonify({"heart_scores": gpt_reply}), 200

    except Exception as e:
        print("❌ SERVER ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500


if __name__ == "__main__":
    # Flask development server on port 10000
    app.run(host="0.0.0.0", port=10000)
