// static/script.js

// ─── 1) Full 15 SPARK questions & emoji options ──────────────────────
const questions = [
  { key: "1", text: "When tasks come with clear structure, you feel…", options: ["⚡ Super-charged","🛑 Short-circuited","🟡 Static","⚠️ Overloaded"] },
  { key: "2", text: "Collaborating with teammates you trust, you feel…", options: ["🤝 Aligned","🔒 Guarded","➡️ Neutral","❓ Exposed"] },
  { key: "3", text: "When you tunnel-vision on a solo project, you feel…", options: ["🔋 Sharpened","🪫 Diffuse","⚖️ Steady","❓ Uncertain"] },
  { key: "4", text: "Guided by our core principles, your dedication feels…", options: ["🚀 Committed","⛔ Resistant","➖ Neutral","❓ Conflicted"] },
  { key: "5", text: "At the start of your day, your energy level is…", options: ["⚡ Fired-up","😴 Drained","🔄 Steady","💤 Lethargic"] },
  { key: "6", text: "When your work aligns with your purpose, you feel…", options: ["🎯 Centered","🌪 Aimless","🟡 Grounded","🌫 Adrift"] },
  { key: "7", text: "Owning your outcomes fully, you feel…", options: ["✅ Effective","❌ Ineffective","🎉 Valued","🙁 Overlooked"] },
  { key: "8", text: "When peers recognize your efforts, you feel…", options: ["👏 Seen","👻 Invisible","🙂 Acknowledged","😐 Neutral"] },
  { key: "9", text: "Being included in team decisions, you feel…", options: ["🤗 Embraced","🚫 Excluded","😌 Accepted","😕 Isolated"] },
  { key: "10", text: "After a high-stress sprint, you feel…", options: ["💪 Bounced-back","😩 Drained","🔄 Stable","😓 Shaky"] },
  { key: "11", text: "Following a recharge (break/weekend), you feel…", options: ["⚡ Fully-charged","😪 Still-tired","🙂 Refreshed","😐 No-change"] },
  { key: "12", text: "When plans shift quickly, you feel…", options: ["🤸 Agile","🧱 Rigid","➖ Neutral","😤 Frustrated"] },
  { key: "13", text: "Striking up a genuine connection, you feel…", options: ["🔗 Bonded","⚪ Alone","🤝 Supported","❔ Detached"] },
  { key: "14", text: "Sharing honest feedback, you feel…", options: ["🔊 Unfiltered","🔒 Reserved","✔️ Clear","😬 Awkward"] },
  { key: "15", text: "Making an impact today, you feel…", options: ["✨ Purposeful","⚪ Ineffective","🚀 Motivated","🙁 Overlooked"] }
];

const answers = {};
let currentQuestionIndex = 0;

const chatWindow = document.getElementById("chatWindow");
const loadingIndicator = document.getElementById("loading");

// ─── Utility: bot bubble ───────────────────────────────────────────
function addBotBubble(text) {
  const bubble = document.createElement("div");
  bubble.className = "bubble bot";
  bubble.innerText = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ─── Utility: user bubble ──────────────────────────────────────────
function addUserBubble(text) {
  const bubble = document.createElement("div");
  bubble.className = "bubble user";
  bubble.innerText = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ─── Render emoji options ──────────────────────────────────────────
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

// ─── Handle user choice ────────────────────────────────────────────
function handleUserChoice(questionKey, chosenText) {
  // remove previous options
  document.querySelectorAll(".options").forEach(el => el.remove());
  // show user bubble
  addUserBubble(chosenText);
  // save answer
  answers[questionKey] = chosenText;
  // next question or submit
  currentQuestionIndex++;
  if (currentQuestionIndex < questions.length) {
    setTimeout(renderNextQuestion, 300);
  } else {
    setTimeout(callScoringAPI, 300);
  }
}

// ─── Show next question ─────────────────────────────────────────────
function renderNextQuestion() {
  const q = questions[currentQuestionIndex];
  addBotBubble(q.text);
  renderOptions(q.options, q.key);
}

// ─── After all answered, call webhook ───────────────────────────────
async function callScoringAPI() {
  loadingIndicator.style.display = "block";

  try {
    // Build payload with the first four SPARK answers under the legacy keys:
    const payload = {
      work_feeling:           answers["1"],   // SPARK question 1
      team_feeling:           answers["2"],   // SPARK question 2
      leadership_feeling:     answers["3"],   // SPARK question 3
      company_people_feeling: answers["4"],   // SPARK question 4
      responses: [answers]                   // all 15 for CTT
    };

    const resp = await fetch("/formester-webhook", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload)
    });

    const data = await resp.json();
    loadingIndicator.style.display = "none";

    // … rest of your success / error handling …


    if (resp.ok) {
      // show H.E.A.R.T.
      addBotBubble("Here are your H.E.A.R.T. scores:");
      const pre1 = document.createElement("pre");
      pre1.innerText = data.heart_scores;
      chatWindow.appendChild(pre1);
      // show CTT
      addBotBubble("Here are your CTT results:");
      const pre2 = document.createElement("pre");
      pre2.innerText = JSON.stringify(data.science_ctt, null, 2);
      chatWindow.appendChild(pre2);
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

// ─── Start the flow on page load ────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  renderNextQuestion();
});