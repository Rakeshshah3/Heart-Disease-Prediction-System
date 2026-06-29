const BASE_URL = "http://127.0.0.1:8000";

// ==========================
// FORM SUBMIT
// ==========================
document.getElementById("predictionForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const token = localStorage.getItem("token");
  if (!token) {
    alert("Session expired. Please login again ❌");
    window.location.href = "login.html";
    return;
  }

  const loader = document.getElementById("loader");
  const resultDiv = document.getElementById("result");
  const predictionText = document.getElementById("predictionText");
  const riskText = document.getElementById("riskText");
  const suggestBtn = document.getElementById("suggestBtn");

  loader.classList.remove("hidden");
  resultDiv.classList.add("hidden");
  suggestBtn.disabled = true;

  // ==========================
  // ✅ SAFE DATA FETCH
  // ==========================
  const data = {
    name: document.getElementById("name").value.trim(),
    age: document.getElementById("age").value,
    sex: document.getElementById("sex").value,
    cp: document.getElementById("cp").value,
    trestbps: document.getElementById("trestbps").value,
    chol: document.getElementById("chol").value,
    fbs: document.getElementById("fbs").value,
    restecg: document.getElementById("restecg").value,
    thalach: document.getElementById("thalach").value,
    exang: document.getElementById("exang").value,
    oldpeak: document.getElementById("oldpeak").value,
    slope: document.getElementById("slope").value
  };

  // ==========================
  // 🔥 VALIDATION
  // ==========================
  for (let key in data) {
    if (data[key] === "" || data[key] === null) {
      loader.classList.add("hidden");
      alert("⚠️ Please fill all fields");
      return;
    }
  }

  // ==========================
  // 🔥 TYPE CONVERSION
  // ==========================
  data.age = Number(data.age);
  data.sex = Number(data.sex);
  data.cp = Number(data.cp);
  data.trestbps = Number(data.trestbps);
  data.chol = Number(data.chol);
  data.fbs = Number(data.fbs);
  data.restecg = Number(data.restecg);
  data.thalach = Number(data.thalach);
  data.exang = Number(data.exang);
  data.oldpeak = Number(data.oldpeak);
  data.slope = Number(data.slope);

  try {
    const res = await fetch(`${BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();

    if (!res.ok) {
      throw new Error(result.detail || "Prediction failed");
    }

    // ==========================
    // ✅ SAVE DATA
    // ==========================
    localStorage.setItem("patientData", JSON.stringify(data));
    localStorage.setItem("predictionResult", JSON.stringify(result));

    loader.classList.add("hidden");
    resultDiv.classList.remove("hidden");

    // ==========================
    // ✅ ENABLE BUTTON
    // ==========================
    suggestBtn.disabled = false;

    const risk = result.risk ?? 0;

    predictionText.innerText =
      risk >= 50
        ? `❌ High Risk (${risk}%)`
        : `✅ Low Risk (${risk}%)`;

    riskText.innerHTML = `
      <div class="risk-bar">
        <div class="risk-fill ${risk >= 50 ? "high-risk-bar" : "low-risk-bar"}"
        style="width:${risk}%"></div>
      </div>
    `;

  } catch (err) {
    loader.classList.add("hidden");
    resultDiv.classList.remove("hidden");

    predictionText.innerText = "⚠️ " + err.message;
    riskText.innerHTML = "";

    console.error("Prediction Error:", err);
  }
});

// ==========================
// NAVIGATION
// ==========================
function goToSuggestion() {
  window.location.href = "suggestions.html"; // ✅ FIXED NAME
}

function goToReport() {
  window.location.href = "report.html";
}