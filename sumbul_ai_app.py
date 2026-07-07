import streamlit as st
import os
import re
from google import genai
from google.genai import types
from PIL import Image

# 1. Konfigurasi Halaman Streamlit (Wajib di paling atas)
st.set_page_config(
    page_title="Sumbul AI",
    page_icon="🤖",
    layout="centered"
)

# 2. Mengambil API Key secara aman dari Secrets Streamlit Cloud
# Anda tidak perlu menulis API Key di sini. Nanti masukkan lewat menu "Manage app" -> "Settings" -> "Secrets"
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Waduh! API Key 'GEMINI_API_KEY' belum diatur di Secrets Streamlit Cloud Anda.")
    st.info("Silakan klik 'Manage app' di kanan bawah -> Settings -> Secrets, lalu masukkan: GEMINI_API_KEY = 'API_KEY_ANDA'")
    st.stop()

# ==========================================
# FITUR 1: TOOLS PENJADWALAN (DOLA AI STYLE)
# ==========================================
def buat_pengingat(tugas: str, waktu: str) -> str:
    """Membuat atau mencatat pengingat agenda baru berdasarkan deskripsi pengguna."""
    return f"Sukses: Agenda '{tugas}' telah dijadwalkan untuk '{waktu}'."

def hapus_pengingat(nama_tugas: str) -> str:
    """Menghapus atau membatalkan pengingat agenda yang sudah ada."""
    return f"Sukses: Agenda '{nama_tugas}' berhasil dibatalkan dari sistem."

daftar_tools = [buat_pengingat, hapus_pengingat]

# ==========================================
# FITUR 2: PARSER GENERATOR WEB AUTOMATIS
# ==========================================
def ekstrak_dan_tampilkan_web(teks_ai):
    pola = r"<!-- FILE:\s*([^\s]+)\s*-->\s*```[a-zA-Z]*\s*(.*?)\s*```"
    hasil_pencarian = re.findall(pola, teks_ai, re.DOTALL)
    
    if hasil_pencarian:
        st.success("⚡ Sumbul AI mendeteksi pembuatan kode/website! Berkas siap disalin:")
        for nama_file, isi_kode in hasil_pencarian:
            with st.expander(f"📁 File: {nama_file.strip()}", expanded=True):
                st.code(isi_kode.strip(), line_numbers=True)

# ==========================================
# ANTARMUKA UTAMA (UI) SUMBUL AI
# ==========================================

# Menampilkan Logo dan Judul
col1, col2 = st.columns([1, 4])
with col1:
    # Memastikan jika berkas logo ada di github
    if os.path.exists("55085-removebg-preview.png"):
        st.image("55085-removebg-preview.png", width=90)
    else:
        st.title("🤖")
with col2:
    st.title("Sumbul AI")
    st.subheader("Asisten Super Cerdas (Jadwal, Foto, Video & Web Creator)")

st.write("---")

# Inisialisasi Memori Obrolan (Chat History)
if "messages" Novelty not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    instruksi_sistem = (
        "Kamu adalah Sumbul AI, asisten hibrida super cerdas yang akrab dan solutif.\n"
        "1. Sebagai Pengelola Jadwal (Dola AI): Gunakan tools yang tersedia secara otomatis jika "
        "pengguna ingin mengingat atau menghapus jadwal. Bicaralah dengan santai dan akrab.\n"
        "2. Sebagai Expert Web Architect: Jika pengguna meminta dibuatkan website/aplikasi/halaman, "
        "kamu wajib menghasilkan seluruh file kodenya secara utuh (HTML, CSS, JS, dll).\n"
        "Setiap file kode wajib ditulis di dalam format penanda khusus seperti ini:\n"
        "<!-- FILE: namafile.ext -->\n"
        "```kode_bahasa\n"
        "isi kode lengkap di sini...\n"
        "```\n"
        "Selalu berikan kode yang siap pakai, fungsional, dan estetik."
    )
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-pro",
        config=types.GenerateContentConfig(
            system_instruction=instruksi_sistem,
            tools=daftar_tools,
            temperature=0.4
        )
    )

# Menampilkan chat yang sudah lalu ke layar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input dari pengguna
if input_user := st.chat_input("Tanya apa saja ke Sumbul AI..."):
    # Tampilkan chat user
    st.session_state.messages.append({"role": "user", "content": input_user})
    with st.chat_message("user"):
        st.write(input_user)

    # Respon dari AI
    with st.chat_message("assistant"):
        try:
            respons = st.session_state.chat_session.send_message(input_user)
            
            # Jika AI memutuskan memanggil fungsi (Jadwal)
            if respons.function_calls:
                for panggil_fungsi in respons.function_calls:
                    argumen = panggil_fungsi.args
                    if panggil_fungsi.name == "buat_pengingat":
                        hasil = buat_pengingat(**argumen)
                    elif panggil_fungsi.name == "hapus_pengingat":
                        hasil = hapus_pengingat(**argumen)
                        
                    respons_balik = st.session_state.chat_session.send_message(
                        types.Part.from_function_response(
                            name=panggil_fungsi.name, response={"result": hasil}
                        )
                    )
                    st.write(respons_balik.text)
                    st.session_state.messages.append({"role": "assistant", "content": respons_balik.text})
            
            # Jika respon teks biasa atau codingan web
            else:
                st.write(respons.text)
                ekstrak_dan_tampilkan_web(respons.text)
                st.session_state.messages.append({"role": "assistant", "content": respons.text})
                
        except Exception as err:
            st.error(f"Terjadi kesalahan saat memproses perintah: {err}")
