#!/usr/bin/env python3
"""
Script untuk menjalankan Sistem Absensi TRPL
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_socketio
        import flask_cors
        import qrcode
        print("✅ Semua dependencies sudah terinstall")
        return True
    except ImportError as e:
        print(f"❌ Dependency tidak ditemukan: {e}")
        print("📦 Install dependencies dengan: pip install -r requirements.txt")
        return False

def main():
    print("🚀 Sistem Absensi TRPL")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if database exists
    if not os.path.exists("absensi.db"):
        print("📊 Database akan dibuat otomatis saat pertama kali menjalankan aplikasi")
    
    print("\n🌐 Menjalankan server...")
    print("📍 Frontend: http://127.0.0.1:5000")
    print("👨‍💼 Admin: http://127.0.0.1:5000/admin/login")
    print("\n📝 Akun Testing:")
    print("   Mahasiswa - NIM: 1234567890, Password: password123")
    print("   Admin - Username: admin, Password: 12345")
    print("\n⏹️  Tekan Ctrl+C untuk menghentikan server")
    print("=" * 50)
    
    # Run the Flask app
    try:
        from absensi_app import app, socketio
        socketio.run(app, debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server dihentikan")
    except Exception as e:
        print(f"❌ Error menjalankan server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

