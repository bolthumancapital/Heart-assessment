# app.py

import os
import json
import traceback

from flask import Flask, request, render_template, redirect, url_for
from openai import OpenAI

app = Flask(__name__)

# ─── 1) Load your OpenAI API key from an environment variable ────────────
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing environment variable: OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


# ───────────────────────────────────────────────────────────────────────────
# ROUTE: GET “/”
#   Serves the HTML form where employees pick four emoji-based responses
# ───────────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    """
    Renders the questionnaire form (index.html).
    """
    return render_template("index.html")


# ───────────────────────────────────────────────────────────────────────────
# ROUTE: POST “/score”
#   Handles the form submission, calls OpenAI to get H.E.A.R.T. scores,
#   then renders result.html with the scores.
# ───────────────────────────────────────────────────────────────────────────
@app.route("/score", methods=["POST"])
def score():
    try:
        # 1) Grab the four answers from the form submission
        q1_answer = request.form.get("work_feeling", "").strip()
        q2_answer = request.form.get("team_feeling", "").strip()
        q3_answer = request.form.get("leadership_feeling", "").strip()
        q4_answer = request.form.get("company_people_feeling", "").strip()

        # 2) Build the prompt (H.E.A.R.T. framework)
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
        # 3) Call OpenAI’s chat endpoint (gpt-3.5-turbo)
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

        # 4) Extract the GPT-generated text
        gpt_reply = response.choices[0].message.content.strip()

        # 5) Pass that reply into result.html for rendering
        return render_template("result.html", heart_scores=gpt_reply)

    except Exception as e:
        # If anything goes wrong, print the error and show a simple error page
        print("❌ SERVER ERROR:", e)
        traceback.print_exc()
        return f"An error occurred: {e}", 500


if __name__ == "__main__":
    # Locally, Flask listens on port 10000
    app.run(host="0.0.0.0", port=10000)
