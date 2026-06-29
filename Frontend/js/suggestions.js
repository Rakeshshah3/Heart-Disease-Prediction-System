const BASE_URL = "http://127.0.0.1:8000";

// ==========================
// 🚀 LOAD SUGGESTION
// ==========================
async function loadSuggestion() {
  try {
    const patientData = JSON.parse(localStorage.getItem("patientData"));
    const token = localStorage.getItem("token");

    if (!token) {
      alert("Session expired ❌");
      window.location.href = "login.html";
      return;
    }

    if (!patientData) {
      setText("planText", "⚠️ No data found.");
      setText("riskText", "No Data ❌");
      return;
    }

    setText("riskText", "⏳ Loading...");
    setText("planText", "Generating plan...");

    const res = await fetch(`${BASE_URL}/suggestion`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(patientData)
    });

    const result = await res.json();

    if (!res.ok) {
      throw new Error(result.detail || "API error");
    }

    // ==========================
    // 🔥 HANDLE RESPONSE
    // ==========================
    let risk = result.risk;

    if (risk === undefined || risk === null) {
      risk = result.prediction === 1 ? 70 : 30;
    }

    // 🛠️ ensure valid number
    risk = Math.round(Number(risk));
    if (isNaN(risk)) risk = 0;

    let plan = result.weekly_plan;

    if (plan && plan.additionalProp1) {
      plan = plan.additionalProp1;
    }

    if (!plan || typeof plan !== "object") {
      plan = generateFallbackPlan(risk);
    }

    // store result
    window.latestResult = {
      risk,
      prediction: result.prediction,
      weekly_plan: plan
    };

    // ==========================
    // ✅ UI UPDATE
    // ==========================
    setText(
      "riskText",
      risk >= 50
        ? `❌ High Risk (${risk}%)`
        : `✅ Low Risk (${risk}%)`
    );

    // ==========================
    // 🔥 FIXED RISK BAR
    // ==========================
    const riskFill = document.getElementById("riskFill");

    if (riskFill) {
      // ensure visible even for low %
      const safeRisk = Math.max(risk, 5);

      riskFill.style.width = `${safeRisk}%`;

      // dynamic color
      if (risk < 40) {
        riskFill.style.background = "#22c55e"; // green
      } else if (risk < 70) {
        riskFill.style.background = "#facc15"; // yellow
      } else {
        riskFill.style.background = "#ef4444"; // red
      }
    }

    renderPlan(plan);

    document.getElementById("downloadBtn").disabled = false;

  } catch (error) {
    console.error("Suggestion Error:", error);
    setText("riskText", "⚠️ Failed");
    setText("planText", "❌ Error loading suggestions.");
  }
}

// ==========================
// 🔥 FALLBACK PLAN
// ==========================
function generateFallbackPlan(risk) {
  const isHigh = risk >= 50;

  const days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
  const plan = {};

  days.forEach(day => {
    plan[day] = {
      diet: isHigh ? "Low salt, avoid oily food" : "Balanced diet",
      exercise: isHigh ? "30 min walking" : "Light exercise",
      precautions: isHigh ? "Avoid stress, regular checkup" : "Maintain routine"
    };
  });

  return plan;
}

// ==========================
// 📊 RENDER PLAN
// ==========================
function renderPlan(plan) {
  const container = document.getElementById("planText");

  container.innerHTML = Object.keys(plan).map(day => {
    const d = plan[day];

    return `
      <div class="day-card">
        <h3>${day}</h3>
        <p><b>🥗 Diet:</b> ${d.diet}</p>
        <p><b>🏃 Exercise:</b> ${d.exercise}</p>
        <p><b>⚠️ Precautions:</b> ${d.precautions}</p>
      </div>
    `;
  }).join("");
}

// ==========================
// 🔧 HELPER
// ==========================
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.innerText = text;
}

// ==========================
// 📥 DOWNLOAD PDF (API)
// ==========================
async function downloadPDF() {
  try {
    const token = localStorage.getItem("token");
    const patientData = JSON.parse(localStorage.getItem("patientData"));
    const result = window.latestResult;

    if (!token || !result) {
      alert("Missing data ❌");
      return;
    }

    const payload = {
      data: patientData,
      prediction: result.prediction,
      weekly_plan: result.weekly_plan
    };

    const res = await fetch(`${BASE_URL}/download-pdf`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error("PDF download failed");
    }

    const blob = await res.blob();

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = "heart_report.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();

  } catch (error) {
    console.error("Download Error:", error);
    alert("Error downloading PDF ❌");
  }
}

// ==========================
// 🎯 INIT
// ==========================
window.addEventListener("DOMContentLoaded", () => {
  loadSuggestion();
  document.getElementById("downloadBtn")
    .addEventListener("click", downloadPDF);
});