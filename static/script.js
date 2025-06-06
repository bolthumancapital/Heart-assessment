// static/script.js

// ─── 1) Questions & their emoji options ────────────────────────────────
const questions = [
  {
    key: "work_feeling",
    text: "Which emoji best captures how you feel about your work right now?",
    options: [
      "😀 Energized",
      "🙂 Okay",
      "😐 Meh",
      "😓 Drained",
      "😡 Frustrated"
    ]
  },
  {
    key: "team_feeling",
    text: "Which emoji best captures how you feel about your team?",
    options: [
      "🤝 Supported",
      "😔 Alone",
      "👂 Heard",
      "❌ Dismissed",
      "🔒 Safe",
      "🤨 Judged",
      "🙌 Encouraged",
      "💡 Valued"
    ]
  },
  {
    key: "leadership_feeling",
    text: "Which emoji best captures how you feel about leadership?",
    options: [
      "🔊 Clear",
      "🙁 Distant",
      "🎯 Trustworthy",
      "☁️ Unclear",
      "✨ Inspiring",
      "🤨 Rigid",
      "😓 Micromanaging",
      "🔒 Safe"
    ]
  },
  {
    key: "company_people_feeling",
    text: "Which emoji best captures how you feel about people at your company?",
    options: [
      "🤗 Included",
      "😒 Ignored",
      "❤️ Connected",
      "🤝 Respectful",
      "🤔 Suspicious",
      "🚪 Excluded",
      "🔒 Safe",
      "😓 Isolated"
    ]
  }
];

// Where we’ll stash each answer:
const answers = {};
let currentQuestionIndex = 0;

const chatWindow = document.getElementById("chatWindow");
const loadingIndicator = document.getElementById("loading");

/* ─── Utility: insert bot bubble ────────────────────────────────────── */
function addBotBubble(text) {
  const bubble = document.createElement("div");
  bubble.className = "bubble bot";
  bubble.innerText = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

/* ─── Utility: insert user bubble ───────────────────────────────────── */
function addUserBubble(text) {
  const bubble = document.createElement("div");
  bubble.className = "bubble user";
  bubble.innerText = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

/* ─── Render emoji option buttons for the current question ─────────── */
function renderOptions(options, questionKey) {
  const container = document.createElement("div");
  container.className = "options";

  options.forEach(opt => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "option-btn";
    btn.innerText = opt;
    btn.onclick = () => handleUserChoice(questionKey, opt);
    container.appendChild(btn);
  });

  chatWindow.appendChild(container);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

/* ─── When the user clicks an emoji answer ───────────────────────────── */
function handleUserChoice(questionKey, chosenText) {
  /* 1) remove previous option buttons */
  document.querySelectorAll(".options").forEach(el => el.remove());

  /* 2) show as user bubble */
  addUserBubble(chosenText);

  /* 3) save answer */
  answers[questionKey] = chosenText;

  /* 4) advance to next question or call the API */
  currentQuestionIndex++;
  if (currentQuestionIndex < questions.length) {
    setTimeout(renderNextQuestion, 400);
  } else {
    setTimeout(callScoringAPI, 400);
  }
}

/* ─── Show next question (bot bubble + options) ─────────────────────── */
function renderNextQuestion() {
  const q = questions[currentQuestionIndex];
  addBotBubble(q.text);
  renderOptions(q.options, q.key);
}

/* ─── After all 4 answered, POST to /formester-webhook ───────────────── */
async function callScoringAPI() {
  loadingIndicator.style.display = "block";

  try {
    const resp = await fetch("/formester-webhook", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(answers)
    });
    const data = await resp.json();
    loadingIndicator.style.display = "none";

    if (resp.ok && data.response) {
      addBotBubble("📊 Here are your H.E.A.R.T. scores:");
      const pre = document.createElement("pre");
      pre.innerText = data.response;
      chatWindow.appendChild(pre);
      chatWindow.scrollTop = chatWindow.scrollHeight;
    } else {
      addBotBubble("⚠️ Sorry, something went wrong. Please try again later.");
    }
  } catch (err) {
    loadingIndicator.style.display = "none";
    addBotBubble("⚠️ Network or server error. Please refresh and try again.");
    console.error(err);
  }
}

/* ─── Kick it all off when the page loads ───────────────────────────── */
window.addEventListener("DOMContentLoaded", () => {
  renderNextQuestion();
});
