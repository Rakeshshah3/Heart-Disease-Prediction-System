const BASE_URL = "http://127.0.0.1:8000";

console.log("✅ script.js loaded");

const form = document.getElementById("predictionForm");
const analyzeBtn = document.getElementById("analyzeBtn");

if (form) {
    form.addEventListener("submit", predict);
}

async function predict(e) {
    e.preventDefault();
    e.stopPropagation();

    console.log("✅ Submit intercepted");

    if (analyzeBtn.disabled) {
        console.log("Duplicate submit blocked");
        return;
    }

    const loader = document.getElementById("loader");
    const resultDiv = document.getElementById("result");
    const predictionText = document.getElementById("predictionText");
    const riskText = document.getElementById("riskText");
    const suggestBtn = document.getElementById("suggestBtn");

    analyzeBtn.disabled = true;
    analyzeBtn.innerText = "Analyzing...";

    const token = localStorage.getItem("token");

    if (!token) {
        alert("Session expired. Please login again.");
        analyzeBtn.disabled = false;
        analyzeBtn.innerText = "🔍 Analyze Risk";
        window.location.href = "login.html";
        return;
    }

    loader.classList.remove("hidden");
    resultDiv.classList.add("hidden");
    if (suggestBtn) suggestBtn.disabled = true;

    const data = {
        name: document.getElementById("name").value.trim(),
        age: Number(document.getElementById("age").value),
        sex: Number(document.getElementById("sex").value),
        cp: Number(document.getElementById("cp").value),
        trestbps: Number(document.getElementById("trestbps").value),
        chol: Number(document.getElementById("chol").value),
        fbs: Number(document.getElementById("fbs").value),
        restecg: Number(document.getElementById("restecg").value),
        thalach: Number(document.getElementById("thalach").value),
        exang: Number(document.getElementById("exang").value),
        oldpeak: Number(document.getElementById("oldpeak").value),
        slope: Number(document.getElementById("slope").value)
    };

    for (const key in data) {
        if (data[key] === "" || data[key] === null || Number.isNaN(data[key])) {
            loader.classList.add("hidden");
            analyzeBtn.disabled = false;
            analyzeBtn.innerText = "🔍 Analyze Risk";
            alert("Please fill all fields.");
            return;
        }
    }

    try {
        console.log("➡️ Sending request");

        const res = await fetch(`${BASE_URL}/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(data)
        });

        console.log("⬅️ Response received");

        const result = await res.json();

        if (!res.ok) {
            // 🔥 Fix for [object Object] error messages
            let errorMsg = "Prediction failed";
            if (Array.isArray(result.detail)) {
                errorMsg = result.detail[0].msg;
            } else if (typeof result.detail === "string") {
                errorMsg = result.detail;
            }
            throw new Error(errorMsg);
        }

        localStorage.setItem("patientData", JSON.stringify(data));
        localStorage.setItem("predictionResult", JSON.stringify(result));

        loader.classList.add("hidden");
        resultDiv.classList.remove("hidden");

        if (suggestBtn) suggestBtn.disabled = false;

        const risk = result.risk || 0;

        predictionText.innerText =
            risk >= 50
                ? `❌ High Risk (${risk}%)`
                : `✅ Low Risk (${risk}%)`;

        riskText.innerHTML = `
            <div class="risk-bar">
                <div class="risk-fill ${risk >= 50 ? "high-risk-bar" : "low-risk-bar"}"
                     style="width:${risk}%">
                </div>
            </div>
        `;

    } catch (err) {
        loader.classList.add("hidden");
        resultDiv.classList.remove("hidden");

        predictionText.innerText = err.message;
        riskText.innerHTML = "";

        console.error(err);

    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerText = "🔍 Analyze Risk";
    }
}

function goToSuggestion() {
    window.location.href = "suggestions.html";
}

function goToReport() {
    window.location.href = "report.html";
}