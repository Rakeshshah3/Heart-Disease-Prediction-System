const BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const msg = document.getElementById("msg");

  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const btn = document.getElementById("loginBtn");

    // ==========================
    // ✅ VALIDATION
    // ==========================
    if (!email || !password) {
      showMsg("Fill all fields ❌", "red");
      return;
    }

    btn.disabled = true;
    btn.innerText = "Logging in...";

    try {
      const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Login failed");
      }

      // ==========================
      // ✅ SAVE TOKEN
      // ==========================
      localStorage.setItem("token", data.access_token);

      showMsg("Login successful 🎉", "#22c55e");

      setTimeout(() => {
        window.location.href = "index.html"; // dashboard
      }, 800);

    } catch (err) {
      showMsg(err.message, "red");
      console.error("Login Error:", err);
    }

    btn.disabled = false;
    btn.innerText = "Login";
  });
});

// ==========================
// 🔧 HELPER
// ==========================
function showMsg(text, color) {
  const msg = document.getElementById("msg");
  if (msg) {
    msg.innerText = text;
    msg.style.color = color;
  }
}