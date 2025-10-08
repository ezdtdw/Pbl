const API_BASE = "http://127.0.0.1:5000"; // arahkan ke Flask, bukan Live Server

document.getElementById("adminLoginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  try {
    const res = await fetch(`${API_BASE}/api/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();
    if (res.ok && data.success) {
      localStorage.setItem("admin_token", data.token);
      window.location.href = "./dashboard.html"; // redirect ke dashboard admin
    } else {
      alert("Login gagal: " + data.message);
    }
  } catch (err) {
    alert("⚠️ Gagal terhubung ke server backend. Pastikan Flask di-port 5000 berjalan!");
  }
});
