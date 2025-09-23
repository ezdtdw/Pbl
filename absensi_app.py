from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_socketio import SocketIO
import sqlite3, qrcode, base64, hashlib, time
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecret"
socketio = SocketIO(app, cors_allowed_origins="*")

DB_NAME = "absensi.db"

# 🔹 Setup database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # tabel mahasiswa
    c.execute("""
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            nim TEXT UNIQUE,
            kelas TEXT,
            password TEXT
        )
    """)

    # tabel sesi absensi
    c.execute("""
        CREATE TABLE IF NOT EXISTS sesi_absen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_sesi TEXT,
            status TEXT,
            jam_mulai TEXT,
            jam_selesai TEXT
        )
    """)

    # tabel absensi
    c.execute("""
        CREATE TABLE IF NOT EXISTS absensi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mahasiswa_id INTEGER,
            sesi_id INTEGER,
            waktu TEXT
        )
    """)

    # tabel admin
    c.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # admin default
    c.execute("SELECT * FROM admin WHERE username=?", ("admin",))
    if not c.fetchone():
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "12345"))

    conn.commit()
    conn.close()

init_db()

# 🔹 QR generator
def generate_token():
    t = int(time.time() // 5)  # token baru tiap 5 detik
    secret = "rahasia123"
    s = f"{t}-{secret}"
    return hashlib.sha256(s.encode()).hexdigest()

def generate_qr_base64(token):
    url = f"http://127.0.0.1:5000/absen?q={token}"
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def qr_updater():
    last_token = None
    while True:
        token = generate_token()
        if token != last_token:
            qr_b64 = generate_qr_base64(token)
            socketio.emit('new_qr', {'qr': qr_b64})
            last_token = token
        socketio.sleep(1)

# -------------------------------
# 🔹 Halaman TV untuk menampilkan QR
@app.route('/')
def index():
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

# -------------------------------
# 🔹 Mahasiswa Register
@app.route('/mahasiswa/register', methods=['GET','POST'])
def mahasiswa_register():
    if request.method == 'POST':
        nama = request.form.get("nama")
        nim = request.form.get("nim")
        kelas = request.form.get("kelas")
        password = request.form.get("password")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO mahasiswa (nama, nim, kelas, password) VALUES (?,?,?,?)",
                      (nama, nim, kelas, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "NIM sudah terdaftar. <a href='/mahasiswa/register'>Coba lagi</a>"
        conn.close()
        return redirect(url_for("mahasiswa_login"))

    return """
    <h2>Register Mahasiswa</h2>
    <form method="post">
      Nama: <input type="text" name="nama"><br><br>
      NIM: <input type="text" name="nim"><br><br>
      Kelas: <input type="text" name="kelas"><br><br>
      Password: <input type="password" name="password"><br><br>
      <button type="submit">Register</button>
    </form>
    """

# 🔹 Mahasiswa Login
@app.route('/mahasiswa/login', methods=['GET','POST'])
def mahasiswa_login():
    if request.method == 'POST':
        nim = request.form.get("nim")
        password = request.form.get("password")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM mahasiswa WHERE nim=? AND password=?", (nim,password))
        user = c.fetchone()
        conn.close()
        if user:
            session['mahasiswa_id'] = user[0]
            return redirect(url_for("mahasiswa_dashboard"))
        else:
            return "Login gagal. <a href='/mahasiswa/login'>Coba lagi</a>"

    return """
    <h2>Login Mahasiswa</h2>
    <form method="post">
      NIM: <input type="text" name="nim"><br><br>
      Password: <input type="password" name="password"><br><br>
      <button type="submit">Login</button>
    </form>
    """

# 🔹 Dashboard Mahasiswa
@app.route('/mahasiswa/dashboard')
def mahasiswa_dashboard():
    if 'mahasiswa_id' not in session:
        return redirect(url_for("mahasiswa_login"))

    mahasiswa_id = session['mahasiswa_id']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM mahasiswa WHERE id=?", (mahasiswa_id,))
    mhs = c.fetchone()
    c.execute("""SELECT s.nama_sesi, a.waktu 
                 FROM absensi a JOIN sesi_absen s ON a.sesi_id=s.id
                 WHERE a.mahasiswa_id=? ORDER BY a.waktu DESC""", (mahasiswa_id,))
    riwayat = c.fetchall()
    conn.close()

    rows = "".join([f"<tr><td>{i+1}</td><td>{r[0]}</td><td>{r[1]}</td></tr>" for i,r in enumerate(riwayat)])

    return f"""
    <h2>Halo, {mhs[1]} (NIM {mhs[2]} | {mhs[3]})</h2>
    <p><a href='/'>📷 Scan QR untuk Absen</a></p>
    <h3>Riwayat Absensi</h3>
    <table border=1 cellpadding=5>
      <tr><th>No</th><th>Sesi</th><th>Waktu</th></tr>
      {rows}
    </table>
    <br>
    <a href='/mahasiswa/logout'>Logout</a>
    """

# 🔹 Proses Absen via QR
@app.route('/absen')
def absen():
    if 'mahasiswa_id' not in session:
        return redirect(url_for("mahasiswa_login"))

    token = request.args.get("q")
    valid_token = generate_token()
    if token != valid_token:
        return "QR tidak valid / expired."

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # cari sesi aktif
    c.execute("SELECT * FROM sesi_absen WHERE status='open'")
    sesi = c.fetchone()
    if not sesi:
        conn.close()
        return "Tidak ada sesi absensi yang sedang dibuka admin."

    mahasiswa_id = session['mahasiswa_id']
    sesi_id = sesi[0]
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # cek apakah sudah absen di sesi ini
    c.execute("SELECT * FROM absensi WHERE mahasiswa_id=? AND sesi_id=?", (mahasiswa_id, sesi_id))
    if c.fetchone():
        conn.close()
        return "Anda sudah absen di sesi ini."

    c.execute("INSERT INTO absensi (mahasiswa_id, sesi_id, waktu) VALUES (?,?,?)",
              (mahasiswa_id, sesi_id, waktu))
    conn.commit()
    conn.close()
    return f"Absensi berhasil dicatat ({sesi[1]} - {waktu}). <a href='/mahasiswa/dashboard'>Kembali</a>"

# 🔹 Logout Mahasiswa
@app.route('/mahasiswa/logout')
def mahasiswa_logout():
    session.pop('mahasiswa_id', None)
    return redirect(url_for("mahasiswa_login"))

# -------------------------------
# 🔹 Admin Login
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get("username")
        pw = request.form.get("password")
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM admin WHERE username=? AND password=?", (user,pw))
        a = c.fetchone()
        conn.close()
        if a:
            session['admin'] = user
            return redirect(url_for("admin_sesi"))
        else:
            return "Login gagal. <a href='/admin/login'>Coba lagi</a>"
    return """
    <h2>Login Admin</h2>
    <form method="post">
      Username: <input type="text" name="username"><br><br>
      Password: <input type="password" name="password"><br><br>
      <button type="submit">Login</button>
    </form>
    """

# 🔹 Admin buka/tutup sesi
@app.route('/admin/sesi', methods=['GET','POST'])
def admin_sesi():
    if 'admin' not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == 'POST':
        if 'buka' in request.form:
            nama = request.form.get("nama_sesi")
            jam_mulai = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO sesi_absen (nama_sesi, status, jam_mulai) VALUES (?, 'open', ?)", (nama, jam_mulai))
        elif 'tutup' in request.form:
            c.execute("UPDATE sesi_absen SET status='closed', jam_selesai=? WHERE id=?",
                      (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request.form.get("sesi_id")))
        conn.commit()

    c.execute("SELECT * FROM sesi_absen ORDER BY id DESC")
    sesi = c.fetchall()
    conn.close()

    rows = "".join([f"<tr><td>{s[0]}</td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td>{s[4]}</td>"
                    + (f"<td><form method='post'><input type='hidden' name='sesi_id' value='{s[0]}'><button name='tutup'>Tutup</button></form></td>" if s[2]=='open' else "<td>-</td>")
                    + "</tr>" for s in sesi])

    return f"""
    <h2>Kelola Sesi Absensi (Admin: {session['admin']})</h2>
    <form method="post">
      Nama Sesi: <input type="text" name="nama_sesi" required>
      <button name="buka">Buka Sesi Baru</button>
    </form>
    <br>
    <table border=1 cellpadding=5>
      <tr><th>ID</th><th>Nama Sesi</th><th>Status</th><th>Jam Mulai</th><th>Jam Selesai</th><th>Aksi</th></tr>
      {rows}
    </table>
    <br>
    <a href='/admin/rekap'>Lihat Rekap</a> | <a href='/admin/logout'>Logout</a>
    """

# 🔹 Admin rekap absensi
@app.route('/admin/rekap')
def admin_rekap():
    if 'admin' not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""SELECT a.id, m.nama, m.nim, s.nama_sesi, a.waktu
                 FROM absensi a 
                 JOIN mahasiswa m ON a.mahasiswa_id=m.id
                 JOIN sesi_absen s ON a.sesi_id=s.id
                 ORDER BY a.waktu DESC""")
    data = c.fetchall()
    conn.close()

    rows = "".join([f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td></tr>" for d in data])

    return f"""
    <h2>Rekap Absensi</h2>
    <table border=1 cellpadding=5>
      <tr><th>ID</th><th>Nama</th><th>NIM</th><th>Sesi</th><th>Waktu</th></tr>
      {rows}
    </table>
    <br>
    <a href='/admin/sesi'>Kembali</a>
    """

# 🔹 Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for("admin_login"))

# -------------------------------
if __name__ == "__main__":
    socketio.start_background_task(qr_updater)
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True, debug=True)
