(function () {
  // Check if user is logged in
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

  // Load student data
  function loadStudentData() {
    try {
      const studentData = JSON.parse(localStorage.getItem('studentData'));
      if (studentData) {
        document.getElementById('welcomeName').textContent = `Selamat Datang, ${studentData.nama}!`;
        document.getElementById('studentNim').textContent = studentData.nim;
        document.getElementById('studentKelas').textContent = studentData.kelas;
        document.getElementById('studentEmail').textContent = studentData.email;
        
        // Set last login time
        const now = new Date();
        document.getElementById('lastLogin').textContent = now.toLocaleString('id-ID');
      }
    } catch (error) {
      console.error('Error loading student data:', error);
    }
  }

  // Logout function
  function logout() {
    if (confirm('Apakah Anda yakin ingin logout?')) {
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('studentData');
      window.location.href = './index.html';
    }
  }

  // QR Scanner functions
  function openQRScanner() {
    document.getElementById('qrModal').classList.remove('hidden');
  }

  function closeQRModal() {
    document.getElementById('qrModal').classList.add('hidden');
  }

  function startQRScan() {
    // TODO: Implement actual QR code scanning
    alert('Fitur QR scanner akan segera tersedia. Untuk sementara, Anda dapat menggunakan fitur absensi melalui web admin.');
    closeQRModal();
  }

  // Show attendance history
  function showAttendanceHistory() {
    alert('Fitur riwayat absensi akan segera tersedia. Data akan diambil dari database.');
  }

  // Show profile
  function showProfile() {
    alert('Fitur profil akan segera tersedia.');
  }

  // Load recent activity
  function loadRecentActivity() {
    // TODO: Load from API
    const activityContainer = document.getElementById('recentActivity');
    activityContainer.innerHTML = `
      <div class="text-center text-gray-500 py-8">
        <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
        </svg>
        <p>Belum ada aktivitas terbaru</p>
        <p class="text-sm mt-2">Data akan dimuat dari database</p>
      </div>
    `;
  }

  // Initialize dashboard
  function initDashboard() {
    if (!checkAuth()) return;
    
    loadStudentData();
    loadRecentActivity();
    
    // Add event listeners
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Make functions globally available
    window.openQRScanner = openQRScanner;
    window.closeQRModal = closeQRModal;
    window.startQRScan = startQRScan;
    window.showAttendanceHistory = showAttendanceHistory;
    window.showProfile = showProfile;
  }

  // Initialize when page loads
  window.addEventListener('load', initDashboard);
})();

