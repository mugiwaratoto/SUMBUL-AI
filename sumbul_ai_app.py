import streamlit as st
import os
import re
import time
from google import genai
from google.genai import types

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA ADVANCED
# ==========================================
st.set_page_config(
    page_title="Sumbul AI - Premium OS",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS Premium untuk Halaman Login dan Chat Bubble
st.markdown("""
    <style>
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FF4B4B, #FF8F8F, #6C5CE7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 1.1rem;
            color: #B0B0B0;
            margin-bottom: 25px;
        }
        .auth-container {
            background: rgba(255, 255, 255, 0.05);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 20px;
        }
        .premium-badge {
            background: linear-gradient(135deg, #D4AF37, #FFD700);
            color: black;
            padding: 5px 12px;
            border-radius: 12px;
            font-weight: 800;
            font-size: 0.75rem;
            display: inline-block;
        }
        .free-badge {
            background-color: #2F3640;
            color: #A4B0BE;
            padding: 5px 12px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.75rem;
            display: inline-block;
        }
        .workspace-card {
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# URL Avatar Grafis / Animasi Bergerak
AVATAR_USER = "👤" 
AVATAR_AI_DIAM = "🤖" 
AVATAR_AI_GERAK = "https://media.giphy.com/media/3v1Sz0oTKRsly/giphy.gif" 

# ==========================================
# 2. SEED STATE & DATABASE LOKAL USER
# ==========================================
# Database akun terdaftar buatan (untuk simulasi pendaftaran username/password)
if "db_users" not in st.session_state:
    st.session_state.db_users = {
        "user123": "password123"  # Akun bawaan contoh awal
    }

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "logged_username" not in st.session_state:
    st.session_state.logged_username = ""

if "user_status" not in st.session_state:
    st.session_state.user_status = "Gratis"

if "total_percakapan" not in st.session_state:
    st.session_state.total_percakapan = 0

if "api_gateway_config" not in st.session_state:
    st.session_state.api_gateway_config = {
        "provider": "Xendit / Midtrans Gateway",
        "mode": "Sandbox",
        "harga_premium": 50000,
        "status_gateway": "Aktif"
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 3. KONEKSI GOOGLE GENAI CLIENT
# ==========================================
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("🔒 Akses Sistem Terkunci: Masukkan 'GEMINI_API_KEY' pada Secrets Streamlit Cloud Anda.")
    st.stop()

# ==========================================
# 4. HALAMAN KHUSUS LOGIN & REGISTRASI (GATEWAY AUTH)
# ==========================================
if not st.session_state.is_logged_in:
    st.markdown('<p class="main-title">Sumbul AI Access Gateway</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Silakan masuk atau buat akun untuk mulai menggunakan Asisten AI</p>', unsafe_allow_html=True)
    
    # Membuat Tab untuk membedakan Menu Login dan Daftar Manual
    tab_login, tab_register, tab_google = st.tabs(["🔐 Login Akun", "📝 Daftar Akun Baru", "🌐 Sign-in with Google"])
    
    with tab_login:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        login_user = st.text_input("Username / Email:", key="log_u")
        login_pass = st.text_input("Password:", type="password", key="log_p")
        if st.button("Masuk Ke Aplikasi", type="primary", use_container_width=True):
            if login_user in st.session_state.db_users and st.session_state.db_users[login_user] == login_pass:
                st.session_state.is_logged_in = True
                st.session_state.logged_username = login_user
                st.success(f"Selamat datang kembali, {login_user}!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Username atau Password salah! Periksa kembali atau daftar akun baru.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab_register:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        reg_user = st.text_input("Buat Username Baru:", key="reg_u")
        reg_pass = st.text_input("Buat Password Aman:", type="password", key="reg_p")
        reg_pass_conf = st.text_input("Ulangi Password:", type="password", key="reg_p_c")
        
        if st.button("Daftarkan Akun", use_container_width=True):
            if not reg_user or not reg_pass:
                st.error("Form pendaftaran tidak boleh kosong!")
            elif reg_user in st.session_state.db_users:
                st.error("Username tersebut sudah terdaftar! Gunakan nama lain.")
            elif reg_pass != reg_pass_conf:
                st.error("Konfirmasi password tidak cocok!")
            else:
                # Simpan akun baru ke database lokal session
                st.session_state.db_users[reg_user] = reg_pass
                st.success("🎉 Pendaftaran Berhasil! Silakan klik Tab 'Login Akun' untuk masuk.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab_google:
        st.markdown('<div class="auth-container" style="text-align:center;">', unsafe_allow_html=True)
        st.write("Hubungkan langsung menggunakan akun Google / Gmail aktif Anda secara instan.")
        
        simulasi_gmail = st.text_input("Masukkan Alamat Gmail Anda:", placeholder="contoh: userbaru@gmail.com", key="g_mail")
        
        if st.button("🌐 Lanjutkan via Google Auth Gateway", use_container_width=True, type="secondary"):
            if "@" in simulasi_gmail and "gmail.com" in simulasi_gmail:
                st.session_state.is_logged_in = True
                st.session_state.logged_username = simulasi_gmail.split("@")[0] # Mengambil nama depan email
                st.toast("Autentikasi Google Berhasil Terhubung!", icon="🌐")
                time.sleep(0.8)
                st.rerun()
            else:
                st.error("Masukkan alamat Gmail yang valid!")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.stop() # Blokir tampilan chat utama jika belum login sukses

# ==========================================
# 5. SIDEBAR PANEL KONTROL INTERAKTIF (SETELAH LOGIN)
# ==========================================
with st.sidebar:
    st.image("55085-removebg-preview.png" if os.path.exists("55085-removebg-preview.png") else "🤖", width=75)
    st.markdown(f"👋 Halo, **{st.session_state.logged_username}**")
    
    if st.session_state.user_status == "Premium":
        st.markdown('<div class="premium-badge">✨ MEMBER PREMIUM VIP</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="free-badge">⚪ PENGGUNA STANDAR</div>', unsafe_allow_html=True)
    
    st.write("---")
    
    pilihan_model = st.selectbox(
        "🧠 Otak AI Aktif:",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0,
        help="Model Pro eksklusif membutuhkan aktivasi Premium via API Gateway"
    )
    
    if pilihan_model == "gemini-2.5-pro" and st.session_state.user_status == "Gratis":
        st.warning("🔒 Model Pro terkunci untuk Akun Gratis.")
        if st.button("💳 Beli Premium Instan", type="primary", use_container_width=True):
            st.session_state.buka_payment_modal = True
            st.rerun()

    suhu_kreativitas = st.slider("🔥 Gaya Bahasa (Kreativitas):", 0.0, 1.0, 0.4, 0.1)
    
    st.write("---")
    if st.button("🚪 Keluar Akun (Log Out)", use_container_width=True, type="secondary"):
        st.session_state.is_logged_in = False
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    with st.expander("🔐 Kontrol Admin Panel", expanded=False):
        if "admin_logged_in" not in st.session_state: st.session_state.admin_logged_in = False
        if not st.session_state.admin_logged_in:
            admin_user = st.text_input("Username:", key="adm_u")
            admin_pass = st.text_input("Password:", type="password", key="adm_p")
            if st.button("Verifikasi Kredensial", use_container_width=True):
                if admin_user == "Yunobi" and admin_pass == "Sembilan9":
                    st.session_state.admin_logged_in = True
                    st.success("Akses Diberikan!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Kredensial Admin Salah!")
        else:
            st.write("Operator: **Yunobi** (Sesi Aktif)")
            if st.button("Keluar Sistem Admin", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.rerun()

# ==========================================
# 6. DASHBOARD UTAMA MANAJEMEN ADMIN
# ==========================================
if "admin_logged_in" in st.session_state and st.session_state.admin_logged_in:
    st.markdown("## 🛠️ Dashboard Administrator Gateway")
    st.caption("Kelola sistem penagihan API Gateway Payment Anda di sini.")
    
    c_adm1, c_adm2 = st.columns(2)
    with c_adm1:
        prov = st.selectbox("API Payment Provider:", ["Midtrans", "Xendit", "Stripe"])
        mode = st.radio("Metode Endpoint:", ["Sandbox / Testing", "Production / Live"])
    with c_adm2:
        harga = st.number_input("Nominal Paket Premium (IDR):", value=int(st.session_state.api_gateway_config["harga_premium"]), step=5000)
        gate_status = st.toggle("Aktifkan Integrasi Sistem", value=True)
        
    if st.button("💾 Amankan & Simpan Perubahan", type="primary", use_container_width=True):
        st.session_state.api_gateway_config = {
            "provider": prov, "mode": mode, "harga_premium": harga, "status_gateway": "Aktif" if gate_status else "Nonaktif"
        }
        st.toast("Konfigurasi API Gateway Disimpan!", icon="💾")
    st.stop()

# ==========================================
# 7. INTEGRASI CHECKOUT GATEWAY PREMIUM USER
# ==========================================
if "buka_payment_modal" in st.session_state and st.session_state.buka_payment_modal:
    st.markdown("### 💳 Secure Payment API Gateway Checkout")
    st.write(f"Provider Gateway: **{st.session_state.api_gateway_config['provider']} ({st.session_state.api_gateway_config['mode']})**")
    st.info(f"Produk: **Lisensi Akun Premium Sumbul AI**\n\nBiaya: **Rp {st.session_state.api_gateway_config['harga_premium']:,}**")
    st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=SumbulPremiumSimulasi", width=150)
    
    cb1, cb2 = st.columns(2)
    with cb1:
        if st.button("✅ Bayar Sekarang (Simulasi Sukses)", use_container_width=True, type="primary"):
            st.session_state.user_status = "Premium"
            st.session_state.buka_payment_modal = False
            st.toast("Pembayaran Terverifikasi! Akun menjadi Premium.", icon="🎉")
            time.sleep(1)
            st.rerun()
    with cb2:
        if st.button("❌ Batalkan Checkout", use_container_width=True):
            st.session_state.buka_payment_modal = False
            st.rerun()
    st.stop()

# ==========================================
# 8. MODEL HANDLERS & KODE PARSER WEB
# ==========================================
def buat_pengingat(tugas: str, Catal_waktu: str) -> str:
    return f"Sukses: Agenda '{tugas}' telah dijadwalkan untuk '{Catal_waktu}'."

def hapus_pengingat(nama_tugas: str) -> str:
    return f"Sukses: Agenda '{nama_tugas}' berhasil dibatalkan dari sistem."

daftar_tools = [buat_pengingat, hapus_pengingat]

def ekstrak_dan_tampilkan_web(teks_ai):
    pola = r"\s*```[a-zA-Z]*\s*(.*?)\s*```"
    hasil_pencarian = re.findall(pola, teks_ai, re.DOTALL)
    if hasil_pencarian:
        st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
        st.markdown("### ⚡ **Sumbul AI Web Workspace**")
        for nama_file, isi_kode in hasil_pencarian:
            with st.expander(f"📁 Berkas kode: {nama_file.strip()}", expanded=True):
                st.code(isi_kode.strip(), line_numbers=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 9. INISIALISASI SESI GENERASI CHAT
# ==========================================
if "chat_session" not in st.session_state:
    instruksi_sistem = (
        "Kamu adalah Sumbul AI, asisten robot anak kecil berwujud digital yang super cerdas, ramah, dan asyik diajak bicara.\n"
        "1. Sebagai Pengelola Jadwal (Dola AI): Jalankan tool 'buat_pengingat' or 'hapus_pengingat' secara otomatis tanpa ragu jika user memberi instruksi waktu.\n"
        "2. Sebagai Expert Web Architect: Jika diminta coding/website, hasilkan arsitektur kode bersih dan utuh menggunakan struktur wajib:\n"
        "\n"
        "```bahasa\nkode\n```"
    )
    st.session_state.chat_session = client.chats.create(
        model=pilihan_model if not (pilihan_model == "gemini-2.5-pro" and st.session_state.user_status == "Gratis") else "gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=instruksi_sistem, tools=daftar_tools, temperature=suhu_kreativitas
        )
    )

# ==========================================
# 10. DISPLAY ANTARMUKA UTAMA CHAT (UI)
# ==========================================
st.markdown('<p class="main-title">Sumbul AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Sistem Integritas AI Hybrid Modern dengan Akses Akun Terproteksi</p>', unsafe_allow_html=True)

# Merender riwayat pesan lama
for message in st.session_state.messages:
    avatar_aktif = AVATAR_USER if message["role"] == "user" else AVATAR_AI_DIAM
    with st.chat_message(message["role"], avatar=avatar_aktif):
        st.write(message["content"])

# Kolom Input Percakapan
input_user = st.chat_input("Ketik instruksi jadwal atau minta buatkan website di sini...")

if input_user:
    if pilihan_model == "gemini-2.5-pro" and st.session_state.user_status == "Gratis":
        st.error("🔒 Akses Ditolak: Anda memilih Otak Pro, silakan aktifkan Akun Premium Anda terlebih dahulu di sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": input_user})
        st.session_state.total_percakapan += 1
        with st.chat_message("user", avatar=AVATAR_USER):
            st.write(input_user)

        with st.chat_message("assistant", avatar=AVATAR_AI_GERAK):
            container_respons = st.empty()
            
            try:
                respons = st.session_state.chat_session.send_message(input_user)
                
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
                        teks_berjalan = ""
                        for huruf in respons_balik.text:
                            teks_berjalan += huruf
                            container_respons.markdown(teks_berjalan + "▌")
                            time.sleep(0.005)
                        container_respons.markdown(respons_balik.text)
                        st.session_state.messages.append({"role": "assistant", "content": respons_balik.text})
                
                else:
                    teks_berjalan = ""
                    for huruf in respons.text:
                        teks_berjalan += huruf
                        container_respons.markdown(teks_berjalan + "▌")
                        time.sleep(0.003)
                    container_respons.markdown(respons.text)
                    
                    ekstrak_dan_tampilkan_web(respons.text)
                    st.session_state.messages.append({"role": "assistant", "content": respons.text})
                    
                st.rerun()
                        
            except Exception as err:
                st.error(f"Sistem mengalami hambatan: {err}")
