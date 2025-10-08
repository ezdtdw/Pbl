(function () {
  const form = document.getElementById('loginForm');
  const nimInput = document.getElementById('nim');
  const passInput = document.getElementById('password');
  const loading = document.getElementById('loadingOverlay');
  const rememberMe = document.getElementById('rememberMe');

  // ✅ ARAHKAN KE BACKEND FLASK (5000), BUKAN 5501/5002
  const API_BASE = "http://127.0.0.1:5000";

  function showLoading(on) {
    loading.classList.toggle('hidden', !on);
  }

  function nimFormatValid(nim) {
    // h233600439 atau 1234567890
    return /^[a-zA-Z]?\d{6,10}$/.test(nim);
  }

  window.addEventListener('load', () => {
    nimInput?.focus();
    try {
      const saved = localStorage.getItem('remember_nim');
      if (saved && nimInput) nimInput.value = saved;
    } catch (_) {}
  });

  nimInput?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') passInput?.focus();
  });

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const nim = nimInput.value.trim();
    const password = passInput.value;

    if (!nim || !password) return alert('Mohon lengkapi semua field!');
    if (!nimFormatValid(nim)) return alert('Format NIM tidak valid! (contoh: h233600439 atau 1234567890)');

    showLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/mahasiswa/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nim, password })
      });

      const data = await res.json();
      showLoading(false);

      if (res.ok && data.success) {
        const studentData = {
          id: data.data.id,
          nim: data.data.nim,
          nama: data.data.nama,
          kelas: data.data.kelas,
          email: `${data.data.nim}@student.ac.id`
        };

        localStorage.setItem('studentData', JSON.stringify(studentData));
        localStorage.setItem('isLoggedIn', 'true');

        try {
          if (rememberMe?.checked) localStorage.setItem('remember_nim', nim);
          else localStorage.removeItem('remember_nim');
        } catch (_) {}

        alert(`Login berhasil! Selamat datang ${data.data.nama} di Sistem Absensi TRPL.`);
        window.location.href = '/frontend/pages/user/dashboard.html';
      } else {
        alert(data.message || 'Login gagal. Silakan coba lagi.');
      }
    } catch (err) {
      showLoading(false);
      console.error(err);
      alert('Gagal terhubung ke server backend. Pastikan Flask berjalan di http://127.0.0.1:5000');
    }
  });
})();
