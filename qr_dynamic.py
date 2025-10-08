from flask import Flask, render_template_string, request, redirect
from flask_socketio import SocketIO
import qrcode, base64, time, hashlib
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

absensi_log = []  # simpan daftar absensi sementara di RAM

def generate_token():
    t = int(time.time() // 2)  # token berubah tiap 2 detik
    secret = "rahasia123"
    s = f"{t}-{secret}"
    token = hashlib.sha256(s.encode()).hexdigest()
    # arahkan ke absensi di server utama (bisa nanti disambungkan ke absensi_app.py)
    return f"http://127.0.0.1:5000/absen?q={token}"

def generate_qr_base64(token):
    img = qrcode.make(token)
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

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Absensi Realtime</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>
        <script>
        document.addEventListener("DOMContentLoaded", () => {
            var socket = io("http://127.0.0.1:5502");
            socket.on("new_qr", function(data) {
                document.getElementById("qr").src = data.qr;
            });
        });
        </script>
    </head>
    <body style="display:flex;justify-content:center;align-items:center;height:100vh;">
        <img id="qr" src="" alt="QR Code absensi" style="max-width:80%;max-height:80%;">
    </body>
    </html>
    """)

@app.route('/absen')
def absen():
    token = request.args.get("q")
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if token:
        absensi_log.append({"token": token, "waktu": waktu})
        print("Absensi tercatat:", token, waktu)
    return redirect("https://politanisamarinda.ac.id/#")

@app.route('/rekap')
def rekap():
    rows = "".join([f"<tr><td>{i+1}</td><td>{a['token']}</td><td>{a['waktu']}</td></tr>" for i,a in enumerate(absensi_log)])
    return f"""
    <h2>Rekap Absensi</h2>
    <table border="1" cellpadding="5">
      <tr><th>No</th><th>Token</th><th>Waktu</th></tr>
      {rows}
    </table>
    """

@app.after_request
def allow_iframe(resp):
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    resp.headers['Content-Security-Policy'] = "frame-ancestors 'self' http://127.0.0.1:5501"
    return resp

if __name__ == '__main__':
    socketio.start_background_task(qr_updater)
    socketio.run(app, host='0.0.0.0', port=5502, allow_unsafe_werkzeug=True)
