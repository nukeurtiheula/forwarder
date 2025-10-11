import asyncio
import random
from telethon import TelegramClient, errors
from dotenv import load_dotenv
import os
import sys

# --- Memuat Konfigurasi ---
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_string = os.getenv("SESSION_STRING")


print("🔎 Memeriksa environment variables...")
if not api_id or not api_hash or not session_string:
    print("❌ FATAL ERROR: Salah satu variabel (API_ID, API_HASH, atau SESSION_STRING) tidak ditemukan.")
    print("   -> Pastikan semua variabel sudah diatur dengan benar di Railway.")
    sys.exit(1) # Menghentikan script dengan pesan error

try:
    api_id = int(api_id)
except (ValueError, TypeError):
    print(f"❌ FATAL ERROR: API_ID harus berupa angka, tapi yang ditemukan adalah: '{api_id}'")
    sys.exit(1)
    
print("✅ Semua environment variables ditemukan dan valid.")

# --- Pengaturan (Dapat Disesuaikan) ---
source_channel = 'kandangpet'
target_groups = [
    'lpmmroblox', 'Lpm_robloxv', 'robloxx_lpm', 'lpmgrowwagarden', 'LPM_ZONA_ROBLOXX', 
    'Chellyra_Lpm', 'kawasanroblox', 'LPMCHEZYW', 'JBGROWAGARDEN1', 'gagtyah', 'LPM_JB_GAGS', 
    'nikelpm', 'lpm_jualan_all', 'growagardenmalays', 'LpmGrowAGardenss',
]
# Menghapus duplikat grup untuk efisiensi
target_groups = list(set(target_groups))

keywords = ['FOR SALE', 'FOR OFFER', 'OPEN BID', 'OPEN JASA']
# Jeda acak antar pengiriman pesan (dalam detik)
delay_per_send_range = (20, 50)
# Jumlah pesan yang diambil dari channel sumber per putaran
jumlah_pesan_diambil = 150
# Jeda acak antar putaran (dalam detik)
delay_antar_loop_range = (400, 700) # Sekitar 6.5 sampai 11.5 menit

# --- Fungsi Utama ---

async def loop_forward(client):
    """Fungsi utama untuk memproses dan meneruskan pesan."""
    print(f"🚀 Auto forwarder aktif! Memantau @{source_channel}")
    print(f"🎯 Total grup target: {len(target_groups)}")
    
    while True:
        try:
            print("\n🔁 Memulai siklus baru... Mengumpulkan pesan yang relevan.")
            source_entity = await client.get_entity(source_channel)
            
            # Langkah 1: Kumpulkan semua pesan yang cocok dengan keyword
            pesan_terkumpul = []
            async for message in client.iter_messages(source_entity, limit=jumlah_pesan_diambil):
                if message.text and any(keyword.lower() in message.text.lower() for keyword in keywords):
                    pesan_terkumpul.append(message)
            
            if not pesan_terkumpul:
                print("ℹ️ Tidak ada pesan dengan keyword yang ditemukan pada siklus ini.")
            else:
                print(f"✅ Berhasil mengumpulkan {len(pesan_terkumpul)} pesan yang relevan.")
                
                # BARU: Langkah 3 - Membuat daftar semua kemungkinan tugas pengiriman.
                # Ini adalah inti dari permintaan Anda: setiap pesan ke setiap grup.
                print("⚙️ Membuat daftar tugas pengiriman lengkap (setiap pesan ke setiap grup)...")
                daftar_tugas_kirim = [
                    (message, group) 
                    for message in pesan_terkumpul 
                    for group in target_groups
                ]
                total_tugas = len(daftar_tugas_kirim)
                print(f"✅ Daftar tugas dibuat. Total {total_tugas} pengiriman akan dilakukan dalam siklus ini.")

                # BARU: Langkah 4 - Mengacak seluruh daftar tugas secara total
                print(f"🔀 Mengacak urutan {total_tugas} tugas...")
                random.shuffle(daftar_tugas_kirim)
                print("🔀 Pengacakan selesai. Memulai proses pengiriman...")

                # BARU: Langkah 5 - Melakukan iterasi pada daftar tugas yang sudah diacak satu per satu
                for i, (message, group_username) in enumerate(daftar_tugas_kirim):
                    print(f"\n▶️ Menjalankan tugas {i+1}/{total_tugas}:")
                    
                    # --- BAGIAN YANG DIPERBAIKI ---
                    # 1. Olah teks pesan di sini, sebelum dimasukkan ke f-string
                    pesan_pratinjau = message.text[:70].replace('\n', ' ')
                    # 2. Gunakan variabel yang sudah diolah di dalam f-string
                    print(f"   Pesan: \"{pesan_pratinjau}...\"")
                    # --- AKHIR PERBAIKAN ---
                    
                    print(f"   Target: @{group_username}")
                    
                    try:
                        # Jeda acak sebelum setiap pengiriman
                        delay = random.uniform(*delay_per_send_range)
                        print(f"   -> Menunggu {delay:.1f} detik...")
                        await asyncio.sleep(delay)
                        
                        await client.forward_messages(group_username, message)
                        print(f"   ✅ Berhasil diteruskan ke @{group_username}")
                        
                    except errors.FloodWaitError as e:
                        print(f"⏳ FLOOD WAIT: Telegram meminta untuk menunggu {e.seconds} detik. Jeda akan dimulai.")
                        await asyncio.sleep(e.seconds + 45) # Tambah jeda ekstra
                        print("⏳ Jeda FloodWait selesai, melanjutkan ke tugas berikutnya.")
                    
                    except (errors.UserIsBlockedError, errors.ChatWriteForbiddenError):
                        print(f"❌ Gagal: Bot diblokir atau tidak memiliki izin di @{group_username}. Melewati tugas ini.")
                    
                    except Exception as e:
                        print(f"❌ Gagal meneruskan ke @{group_username}: {type(e).__name__} - {e}")

            # Jeda antar siklus
            loop_delay = random.uniform(*delay_antar_loop_range)
            print(f"\n✅ SIKLUS INI SELESAI. Semua tugas telah dieksekusi.")
            print(f"🕒 Menunggu {loop_delay/60:.1f} menit sebelum memulai siklus berikutnya...")
            await asyncio.sleep(loop_delay)

        except errors.FloodWaitError as e:
            print(f"⏳ FLOOD WAIT (level siklus): Menunggu {e.seconds} detik...")
            await asyncio.sleep(e.seconds + 60)
            
        except Exception as e:
            print(f"⚠️ Terjadi error tidak terduga di loop utama: {e}")
            print("⚠️ Mencoba lagi dalam 60 detik...")
            await asyncio.sleep(60)

# GANTI SELURUH FUNGSI main() DENGAN INI

async def main():
    """Menjalankan klien Telegram dan menangani koneksi ulang."""
    session_string = os.getenv("SESSION_STRING") # Mengambil kunci sesi dari environment

    while True:
        try:
            # Menggunakan StringSession, bukan nama file
            print("❤️ Mencoba menghubungkan ke Telegram...")
            async with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
                # ---> LIHAT DI SINI, BARIS INI DAN DI BAWAHNYA MENJOROK KE DALAM
                print("✅ Berhasil terhubung menggunakan session string.")
                await loop_forward(client)
                
        except Exception as e:
            print(f"❌ Klien terputus atau gagal terhubung: {e}")
            print("🔌 Mencoba menghubungkan kembali dalam 20 detik...")
            await asyncio.sleep(20)