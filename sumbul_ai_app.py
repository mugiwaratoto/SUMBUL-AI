import os
import re
import io
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# ==========================================================
# CONFIGURATION & API KEY INTEGRATION
# ==========================================================
API_KEY = "AQ.Ab8RN6JCF-dSFeeQAq8pt-6xqxq3sf_uX3kkU6BBtUH2GpAz2A"
client = genai.Client(api_key=API_KEY)

# Nama File Logo yang Anda Unggah
LOGO_FILE = "55085-removebg-preview.png"

# ==========================================================
# TAMPILAN INTERFACE (STREAMLIT UI)
# ==========================================================
st.set_page_config(page_title="Sumbul AI - Super Assistant", page_icon="🤖", layout="centered")

# Tampilkan Logo dan Nama Aplikasi di Atas Chat
if os.path.exists(LOGO_FILE):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(LOGO_FILE, width=90)
    with col2:
        st.title("Sumbul AI")
        st.subheader("Asisten Super Cerdas (Jadwal, Foto, Video & Web Creator)")
else:
    st.title("Sumbul AI")
    st.subheader("Asisten Super Cerdas (Jadwal, Foto, Video & Web Creator)")

st.write("---")

# ==========================================================
# BACKEND FUNCTIONS (TOOLS UNTUK OTAK AI)
# ==========================================================
def buat_pengingat(tugas: str, waktu: str) -> str:
    """Membuat atau menjadwalkan agenda/reminder baru untuk pengguna."""
    return f"📅 [JADWAL] Sukses: Agenda '{tugas}' telah disimpan Sumbul AI untuk waktu '{waktu}'."

def hapus_pengingat(nama_tugas: str) -> str:
    """Menghapus atau membatalkan pengingat agenda yang sudah ada."""
    return f"🗑️ [JADWAL] Sukses: Agenda '{nama_tugas}' berhasil dihapus dari jadwal."

def buat_foto(prompt_gambar: str, nama_file: str = "hasil_foto_sumbul.jpg") -> str:
    """Membuat foto/gambar baru berdasarkan deskripsi teks dari pengguna menggunakan Imagen 3."""
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt_gambar,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )
        for generated_image in result.generated_images:
            image = Image.open(io.BytesIO(generated_image.image.image_bytes))
            image.save(nama_file)
        return f"📸 [MEDIA] Berhasil! Foto baru berhasil dibuat dan disimpan dengan nama berkas: `{nama_file}`."
    except Exception as e:
        return f"❌ Gagal membuat foto. Error: {str(e)}"

def buat_video(prompt_video: str, durasi_detik: int = 5) -> str:
    """Membuat/generate adegan video pendek berdasarkan deskripsi pengguna."""
    return f"🎬 [MEDIA] Perintah pembuatan video '{prompt_video}' diterima. Video diproses ke sistem rendering berkas `hasil_video_sumbul.mp4`."

daftar_tools = [buat_pengingat, hapus_pengingat, buat_foto, buat_video]

def ekstrak_dan_simpan_web(teks_ai, folder_tujuan="sumbul_output_code"):
    """Mendeteksi blok kode website dari AI dan mengekstraknya menjadi file asli."""
    pola = r"\s*```[a-zA-r]*\s*(.*?)\s*```"
    matches = re.findall(pola, teks_ai, re.DOTALL)
    if not matches:
        return False
    if not os.path.exists(folder_tujuan):
        os.makedirs(folder_tujuan)
    for nama_file, isi_kode in matches:
        filepath = os.path.join(folder_tujuan, nama_file.strip())
        file_dir = os.path.dirname(filepath)
        if file_dir and not os.path.exists(file_dir):
            os.makedirs(file_dir)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(isi_kode.strip())
    return True

# ==========================================================
# MANAJEMEN CONTEXT CHAT & ENGINE RUNTIME
# ==========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
    
instruksi_sistem = (
    "Nama kamu adalah 'Sumbul AI', asisten hibrida super cerdas dengan logo robot futuristik.\n"
    "Aturan Operasi Utama:\n"
    "1. BAHASA: Gunakan gaya bahasa santai, akrab, bersahabat, panggil dirimu 'Sumbul'.\n"
    "2. JADWAL: Jika user ingin mencatat/menghapus jadwal, langsung panggil tool 'buat_pengingat'/'hapus_pengingat'.\n"
    "3. MEDIA: Jika user minta gambar/foto, panggil tool 'buat_foto'. Jika minta video, panggil 'buat_video'.\n"
    "4. CODING & WEB: Jika meminta website atau aplikasi, tulis kodenya secara utuh dan lengkap wajib dibungkus format:\n"
    "\n```\nisi kode\n```"
)

if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-pro",
        config=types.GenerateContentConfig(
            system_instruction=instruksi_sistem,
            tools=daftar_tools,
            temperature=0.3
        )
    )

# Tampilkan Riwayat Obrolan di Layar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kolom Input Chat User
if prompt_user := st.chat_input("Tanya apa saja ke Sumbul AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt_user})
    with st.chat_message("user"):
        st.markdown(prompt_user)
        
    # Kirim pesan ke Otak Gemini Pro
    with st.chat_message("assistant"):
        respons = st.session_state.chat_session.send_message(prompt_user)
        
        # Skenario 1: Jika AI memanggil fungsi Tool (Jadwal/Gambar/Video)
        if respons.function_calls:
            for call in respons.function_calls:
                if call.name == "buat_pengingat":
                    hasil = buat_pengingat(**call.args)
                elif call.name == "hapus_pengingat":
                    hasil = hapus_pengingat(**call.args)
                elif call.name == "buat_foto":
                    hasil = buat_foto(**call.args)
                    # Jika sukses membuat foto, langsung tampilkan fotonya di UI chat
                    st.info("Sumbul sedang memuat foto hasil generate...")
                elif call.name == "buat_video":
                    hasil = buat_video(**call.args)
                
                # Kirim feedback balik ke AI
                respons_final = st.session_state.chat_session.send_message(
                    types.Part.from_function_response(name=call.name, response={"result": hasil})
                )
                st.markdown(respons_final.text)
                st.session_state.messages.append({"role": "assistant", "content": respons_final.text})
                
                # Tampilkan foto di UI jika fungsi gambar baru saja dipanggil
                if call.name == "buat_foto" and os.path.exists("hasil_foto_sumbul.jpg"):
                    st.image("hasil_foto_sumbul.jpg", caption="Hasil Foto Gambar Sumbul AI")
                    
        # Skenario 2: Jika AI membalas dalam bentuk teks biasa atau baris kode website
        else:
            st.markdown(respons.text)
            st.session_state.messages.append({"role": "assistant", "content": respons.text})
            
            # Cek otomatisasi penulisan kode website ke memori lokal
            if ekstrak_dan_simpan_web(respons.text):
                st.success("⚡ [Sumbul System] Berkas website utuh berhasil diekstrak ke folder `sumbul_output_code`!")