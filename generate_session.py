# generate_session.py (Versi Aman)

from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os

# Memuat variabel dari file .env
load_dotenv()

print("Membaca API_ID dan API_HASH dari file .env...")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

# Memastikan variabel ada
if not api_id or not api_hash:
    raise ValueError("Pastikan API_ID dan API_HASH sudah diatur di file .env")

print("Mencoba membuat sesi string...")

# Memulai klien dan proses login interaktif
with TelegramClient(StringSession(), int(api_id), api_hash) as client:
    session_string = client.session.save()
    print("\nLogin berhasil! Ini adalah session string-mu (RAHASIA!):")
    print(f"\n{session_string}\n")
    print("✅ Simpan string di atas. Kamu akan membutuhkannya di Railway.")