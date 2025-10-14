from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import sqlite3, qrcode, base64, hashlib, time, os
from io import BytesIO
from datetime import datetime

# ======================
# 🔹 Konfigurasi Flask
# ======================
app = Flask(__name__)
app.secret_key = "supersecret"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 🔹 Path absolut agar kompatibel di hosting
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "absensi.db")

# ======================
# 🔹 Setup database
# ======================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            nim TEXT UNIQUE,
            kelas TEXT,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sesi_absen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_sesi TEXT,
            status TEXT,
            jam_mulai TEXT,
            jam_selesai TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS absensi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mahasiswa_id INTEGER,
            sesi_id INTEGER,
            waktu TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Admin default
    c.execute("SELECT * FROM admin WHERE username=?", ("admin",))
    if not c.fetchone():
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "12345"))

    # Sample mahasiswa
    samples = [
        ("Ahmad Rizki Pratama", "1234567890", "TRPL-2B", "password123"),
        ("Siti Nurhaliza", "0987654321", "TRPL-2A", "password123"),
    ]
    for nama, nim, kelas, pw in samples:
        c.execute("SELECT * FROM mahasiswa WHERE nim=?", (nim,))
        if not c.fetchone():
            c.execute("INSERT INTO mahasiswa (nama, nim, kelas, password) VALUES (?, ?, ?, ?)", (nama, nim, kelas, pw))

    conn.commit()
    conn.close()

init_db()

# ======================
# 🔹 Serve Frontend (HTML/JS/CSS)
# ======================
@app.route('/')
def serve_index():
    return send_from_directory(os.path.join(BASE_DIR, 'frontend', 'pages', 'user'), 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(BASE_DIR, filename)
    return jsonify({"error": "File tidak ditemukan"}), 404

# ======================
# 🔹 QR Generator
# ======================
def generate_token():
    t = int(time.time() // 5)
    secret = "rahasia123"
    s = f"{t}-{secret}"
    return hashlib.sha256(s.encode()).hexdigest()

def generate_qr_base64(token):
    base_url = "https://payabsen.my.id/flaskapp"
    url = f"{base_url}/absen?q={token}"
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

@app.route('/api/qrcode')
def generate_qr():
    data = "absensi_sesi_2025"
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return jsonify({"qr_code": qr_base64})

def qr_updater():
    last_token = None
    while True:
        token = generate_token()
        if token != last_token:
            qr_b64 = generate_qr_base64(token)
            socketio.emit('new_qr', {'qr': qr_b64})
            last_token = token
        socketio.sleep(1)

@app.route('/tv')
def tv_display():
    return render_template_string("""
    <h2>QR Absensi Realtime</h2>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>
    <script>
    document.addEventListener("DOMContentLoaded", () => {
        var socket = io();
        socket.on("new_qr", function(data) {
            document.getElementById("qr").src = data.qr;
        });
    });
    </script>
    <img id="qr" src="" alt="QR Code absensi" style="max-width:60%;margin-top:20px;">
    """)

# ======================
# 🔹 API LOGIN Mahasiswa
# ======================
@app.route('/api/mahasiswa/login', methods=['POST'])
def api_mahasiswa_login():
    try:
        data = request.get_json()
        nim = data.get('nim')
        password = data.get('password')

        if not nim or not password:
            return jsonify({'success': False, 'message': 'NIM dan password harus diisi'}), 400

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM mahasiswa WHERE nim=? AND password=?", (nim, password))
        user = c.fetchone()
        conn.close()

        if user:
            student_data = {'id': user[0], 'nama': user[1], 'nim': user[2], 'kelas': user[3]}
            return jsonify({'success': True, 'message': 'Login berhasil', 'data': student_data})
        else:
            return jsonify({'success': False, 'message': 'NIM atau password salah'}), 401
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'message': 'Terjadi kesalahan server'}), 500

# ======================
# 🔹 API LOGIN Admin
# ======================
@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    admin_user = "admin"
    admin_pass_hash = hashlib.sha256("12345".encode()).hexdigest()

    if username == admin_user and hashlib.sha256(password.encode()).hexdigest() == admin_pass_hash:
        return jsonify({"success": True, "message": "Login berhasil", "token": "ADMIN-SESSION-TRPL-2025"})
    else:
        return jsonify({"success": False, "message": "Username atau password salah"}), 401

# ======================
# 🔹 WSGI Entry Point
# ======================
if __name__ != "__main__":
    socketio.start_background_task(qr_updater)
else:
    socketio.start_background_task(qr_updater)
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True, debug=True)
