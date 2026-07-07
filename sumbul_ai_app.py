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
            margin-top: 10px;
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
# Berfungsi sebagai memori penyimpanan akun terdaftar sementara
if "db_users" not in st.session_state:
    st.session_state.db_users = {
        "admin": "admin123"  # Akun default bawaan sistem untuk uji coba
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

# State pembantu untuk perpindahan tab otomatis pasca registrasi
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0

if "prefilled_user" not in st.session_state:
    st.session_state.prefilled_user = ""

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
# 4. HALAMAN HUBUNGAN GATEWAY AUTH
# ==========================================
if not st.session_state.is_logged_in:
    st.markdown('<p class="main-title">Sumbul AI Access Gateway</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Silakan masuk atau daftarkan akun baru Anda</p>', unsafe_allow_html=True)
    
    # Mengontrol indeks tab secara dinamis berdasarkan alur registrasi user
    pilihan_tab = ["🔐 Login Akun", "📝 Daftar Akun Baru", "🌐 Sign-in with Google"]
    tab_aktif = st.radio("Pilih Menu Autentikasi:", pilihan_tab, horizontal=True, label_visibility="collapsed")
    
    if tab_aktif == "🔐 Login Akun":
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown("### Masuk ke Aplikasi")
        
        # Jika user baru daftar, kolom ini otomatis terisi username barunya
        login_user = st.text_input("Username / Email:", value=st.session_state.prefilled_user, key="log_u")
        login_pass = st.text_input("Password:", type="password", key="log_p")
        
        if st.button("Masuk Sekarang", type="primary", use_container_width=True):
            if login_user in st.session_state.db_users and st.session_state.db_users[login_user] == login_pass:
                st.session_state.is_logged_in = True
                st.session_state.logged_username = login_user
                st.success(f"Selamat datang kembali, {login_user}!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Username atau Password salah! Silakan periksa kembali akun Anda.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    elif tab_aktif == "📝 Daftar Akun Baru":
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown("### Registrasi Akun Pengguna Baru")
        reg_user = st.text_input("Buat Username Baru:", key="reg_u")
        reg_pass = st.text_input("Buat Password Aman:", type="password", key="reg_p")
        reg_pass_conf = st.text_input("Konfirmasi Password:", type="password", key="reg_p_c")
        
        if st.button("Daftarkan Akun", use_container_width=True, type="primary"):
            if not reg_user or not reg_pass:
                st.error("Form pendaftaran tidak boleh kosong!")
            elif reg_user in st.session_state.db_users:
                st.error("Username tersebut sudah terdaftar! Gunakan nama lain.")
            elif reg_pass != reg_pass_conf:
                st.error("Konfirmasi password tidak sesuai!")
            else:
                # Memasukkan akun baru ke dalam database lokal
                st.session_state.db_users[reg_user] = reg_pass
                # Mengisi prefilled agar di menu login user tidak repot mengetik ulang username
                st.session_state.prefilled_user = reg_user
                st.success(f"🎉 Registrasi Sukses untuk '{reg_user}'! Akun Anda telah aktif. Silakan beralih ke menu 'Login Akun' di atas untuk masuk.")
                st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)
        
    elif tab_aktif == "🌐 Sign-in with Google":
        st.markdown('<div class="auth-container" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("### Google Auth Gateway")
        st.write("Hubungkan sistem dengan akun Google / Gmail aktif Anda secara instan.")
        
        simulasi_gmail = st.text_input("Masukkan Alamat Gmail Anda:", placeholder="contoh: budi@gmail.com", key="g_mail")
        
        if st.button("🌐 Lanjutkan Akses via Google Account", use_container_width=True):
            if "@" in simulasi_gmail and "gmail.com" in simulasi_gmail:
                nama_depan = simulasi_gmail.split("@")[0]
                st.session_state.db_users[nama_depan] = "oauth_verified_account"
                st.session_state.is_logged_in = True
                st.session_state.logged_username = nama_depan
                st.toast("Autentikasi Akun Google Berhasil Terhubung!", icon="🌐")
                time.sleep(0.8)
                st.rerun()
            else:
                st.error("Masukkan format alamat Gmail yang valid!")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.stop() # Cegah user mengakses halaman obrolan sebelum sukses terverifikasi

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
        st.session_state.prefilled_user = ""
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
            st.toast("Pembayaran Terverifikasi! Akun menjadi Premium.", icon="
