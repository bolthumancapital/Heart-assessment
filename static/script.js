document.getElementById("heartForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q1 = document.getElementById("q1").value;
  const q2 = document.getElementById("q2").value;
  const q3 = document.getElementById("q3").value;
  const q4 = document.getElementById("q4").value;

  // Build the JSON payload exactly how our Flask endpoint expects it
  const payload = {
    data: {
      submission: {
        "How does your work feel right now?": q1,
        "How do you feel about your team?": q2,
        "How do you feel about leadership?": q3,
        "Which emoji best captures how you feel about people at your company?": q4,
      },
    },
  };

  // Replace <YOUR-RENDER-URL> with your actual Render URL
  const renderUrl = "https://<YOUR-RENDER-SERVICE>.onrender.com/formester-webhook";

  try {
    const res = await fetch(renderUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    document.getElementById("result").textContent = data.response;
  } catch (error) {
    document.getElementById("result").textContent = "Error: " + error.message;
  }
});
