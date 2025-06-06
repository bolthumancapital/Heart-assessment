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
        # 1) Log the full incoming payload
        incoming = request.json
        print("➡️ Incoming Formester payload:\n", json.dumps(incoming, indent=2))

        # 2) Navigate to the "submission" dict
        data = incoming.get("data", {})
        submission = data.get("submission", {})
        if not submission:
            print("❌ ERROR: No 'submission' field found.")
            return jsonify({"error": "No submission data received."}), 400

        # 3) Define the exact question labels
        q1_label = "How does your work feel right now?"
        q2_label = "How do you feel about your team?"
        q3_label = "How do you feel about leadership?"
        q4_label = "Which emoji best captures how you feel about people at your company?"

        # 4) Extract answers, handling list→string conversion
        _raw1 = submission.get(q1_label, "")
        if isinstance(_raw1, list) and len(_raw1) > 0:
            q1_answer = _raw1[0].strip()
        else:
            q1_answer = str(_raw1).strip()

        _raw2 = submission.get(q2_label, "")
        if isinstance(_raw2, list) and len(_raw2) > 0:
            q2_answer = _raw2[0].strip()
        else:
            q2_answer = str(_raw2).strip()

        _raw3 = submission.get(q3_label, "")
        if isinstance(_raw3, list) and len(_raw3) > 0:
            q3_answer = _raw3[0].strip()
        else:
            q3_answer = str(_raw3).strip()

        _raw4 = submission.get(q4_label, "")
        if isinstance(_raw4, list) and len(_raw4) > 0:
            q4_answer = _raw4[0].strip()
        else:
            q4_answer = str(_raw4).strip()

        # 5) Debug print
        print("📝 Extracted Answers:")
        print(f"    {q1_label} → {q1_answer}")
        print(f"    {q2_label} → {q2_answer}")
        print(f"    {q3_label} → {q3_answer}")
        print(f"    {q4_label} → {q4_answer}")

        missing = [lbl for lbl, ans in [
            (q1_label, q1_answer),
            (q2_label, q2_answer),
            (q3_label, q3_answer),
            (q4_label, q4_answer)
        ] if ans == ""]
        if missing:
            print("⚠️ WARNING: These questions were blank or missing:", missing)

        # 6) Build the GPT prompt
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

        # 8) Return to Formester
        return jsonify({"response": gpt_reply}), 200

    except Exception as e:
        print("❌ SERVER ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "Server error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
