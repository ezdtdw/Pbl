# Sistem Absensi TRPL

Sistem absensi modern berbasis QR Code untuk Program Studi Teknologi Rekayasa Perangkat Lunak.

## Fitur

- ✅ Login mahasiswa dengan database
- ✅ Dashboard mahasiswa
- ✅ Sistem QR Code untuk absensi
- ✅ Admin panel untuk mengelola sesi absensi
- ✅ Riwayat absensi mahasiswa
- ✅ Interface modern dengan Tailwind CSS

## Instalasi

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd Pbl-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi**
   ```bash
   python absensi_app.py
   ```

4. **Akses aplikasi**
   - Frontend: http://127.0.0.1:5000
   - Admin: http://127.0.0.1:5000/admin/login

## Akun Testing

### Mahasiswa
- **NIM:** 1234567890
- **Password:** password123
- **Nama:** Ahmad Rizki Pratama
- **Kelas:** TRPL-2B

- **NIM:** 0987654321
- **Password:** password123
- **Nama:** Siti Nurhaliza
- **Kelas:** TRPL-2A

### Admin
- **Username:** admin
- **Password:** 12345

## Struktur Database

### Tabel Mahasiswa
- `id` - Primary Key
- `nama` - Nama lengkap mahasiswa
- `nim` - Nomor Induk Mahasiswa (unique)
- `kelas` - Kelas mahasiswa
- `password` - Password login

### Tabel Sesi Absen
- `id` - Primary Key
- `nama_sesi` - Nama sesi absensi
- `status` - Status sesi (aktif/nonaktif)
- `jam_mulai` - Waktu mulai sesi
- `jam_selesai` - Waktu selesai sesi

### Tabel Absensi
- `id` - Primary Key
- `mahasiswa_id` - Foreign Key ke tabel mahasiswa
- `sesi_id` - Foreign Key ke tabel sesi_absen
- `waktu` - Waktu absensi

## API Endpoints

### Mahasiswa
- `POST /api/mahasiswa/login` - Login mahasiswa
- `GET /mahasiswa/dashboard` - Dashboard mahasiswa
- `GET /mahasiswa/logout` - Logout mahasiswa

### Admin
- `GET /admin/login` - Halaman login admin
- `POST /admin/login` - Proses login admin
- `GET /admin/sesi` - Kelola sesi absensi

## Teknologi yang Digunakan

- **Backend:** Python Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS (Tailwind), JavaScript
- **QR Code:** qrcode library
- **Real-time:** Flask-SocketIO

## Cara Penggunaan

1. **Login sebagai Mahasiswa**
   - Buka http://127.0.0.1:5000
   - Masukkan NIM dan password
   - Klik "Masuk ke Dashboard"

2. **Login sebagai Admin**
   - Buka http://127.0.0.1:5000/admin/login
   - Masukkan username dan password admin
   - Kelola sesi absensi

3. **Absensi dengan QR Code**
   - Admin membuat sesi absensi
   - QR code akan muncul di halaman utama
   - Mahasiswa scan QR code untuk absen

## Troubleshooting

### Error CORS
Jika mengalami error CORS, pastikan Flask-CORS sudah terinstall:
```bash
pip install Flask-CORS
```

### Database tidak ditemukan
Database akan dibuat otomatis saat pertama kali menjalankan aplikasi.

### Port sudah digunakan
Jika port 5000 sudah digunakan, ubah di file `absensi_app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Ganti port
```

## Kontribusi

1. Fork repository
2. Buat branch fitur baru
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request

## Lisensi

MIT License

