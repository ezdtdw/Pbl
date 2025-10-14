(function () {
  function checkAuth() {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const studentData = localStorage.getItem('studentData');
    if (!isLoggedIn || !studentData) {
      alert('Anda belum login. Silakan login terlebih dahulu.');
      window.location.href = './index.html';
      return false;
    }
    return true;
  }

  function loadStudentData() {
    const studentData = JSON.parse(localStorage.getItem('studentData'));
    if (studentData) {
      document.getElementById('welcomeName').textContent = `Selamat Datang, ${studentData.nama}!`;
      document.getElementById('studentNim').textContent = studentData.nim;
      document.getElementById('studentKelas').textContent = studentData.kelas;
      document.getElementById('studentEmail').textContent = studentData.email;
      document.getElementById('lastLogin').textContent = new Date().toLocaleString('id-ID');
    }
  }

  function logout() {
    if (confirm('Apakah Anda yakin ingin logout?')) {
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('studentData');
      window.location.href = './index.html';
    }
  }

  function initDashboard() {
    if (!checkAuth()) return;
    loadStudentData();
    document.getElementById('logoutBtn').addEventListener('click', logout);
  }

  window.addEventListener('load', initDashboard);
})();
