import streamlit as st
import streamlit.components.v1 as components
import re
from google import genai
from google.genai import types

# --- 1. KONFIGURASI TEMA & HALAMAN ---
st.set_page_config(
    page_title="Sumbul AI OS",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS untuk UI minimalis ala Gemini
st.markdown("""
    <style>
    /* Styling input agar terlihat rounded dan bersih */
    [data-testid="stChatInput"] {
        border-radius: 25px;
        border: 1px solid #d1d5db;
        padding: 5px 15px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    /* Styling tombol chat */
    button[kind="primary"] { border-radius: 50% !important; }
    
    /* Container Login */
    .login-box {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIKA STATE ---
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

# --- 3. FUNGSI PENJADWALAN (AI TOOLS) ---
def buat_pengingat(tugas, waktu): 
    return f"✅ Berhasil! '{tugas}' dijadwalkan pada '{waktu}'."

# --- 4. FUNGSI CORE AI ---
def get_chat_session():
    if "chat_session" not in st.session_state:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.chat_session = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction="Kamu asisten Sumbul AI. Jika user minta web, buat HTML di dalam ```html ... ```."
            )
        )
    return st.session_state.chat_session

def extract_web_code(text):
    match = re.search(r"```html(.*?)```", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None

# --- 5. UI LOGIN ---
if not st.session_state.is_logged_in:
    st.markdown('<div class="login-box"><h2>🔐 Masuk ke Sumbul AI</h2>', unsafe_allow_html=True)
    user = st.text_input("", placeholder="Masukkan Username...")
    if st.button("Masuk", use_container_width=True):
        st.session_state.is_logged_in = True
        st.session_state.username = user
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 6. DASHBOARD UTAMA ---
st.title(f"🤖 Sumbul AI | {st.session_state.username}")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Percakapan")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])
            
    if prompt := st.chat_input("Apa yang bisa saya bantu hari ini?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            chat = get_chat_session()
            response = chat.send_message(prompt)
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            if code := extract_web_code(response.text):
                st.session_state.last_code = code
                st.rerun()

with col2:
    st.subheader("Live Web Sandbox")
    if "last_code" in st.session_state:
        components.html(st.session_state.last_code, height=600, scrolling=True)
        if st.download_button("💾 Download Hasil", st.session_state.last_code, "web.html"):
            st.success("Berhasil!")
    else:
        st.info("Minta AI buat website, dan hasilnya akan muncul di sini secara otomatis.")
