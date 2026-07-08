import streamlit as st
import re
from google import genai
from google.genai import types

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Sumbul AI - Premium OS", page_icon="🤖", layout="wide")

# CSS PREMIUM & GAUL
st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 10px; }
    .feature-box { background: #f9f9f9; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #ddd; margin: 5px; }
    [data-testid="stChatInput"] { border-radius: 25px; }
    </style>
""", unsafe_allow_html=True)

# 2. LOGIKA AI GAUL
def get_chat():
    if "chat_session" not in st.session_state:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.chat_session = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Lo adalah Sumbul AI, asisten paling kece di 2026. "
                    "Bahasa lo harus gaul, santai, tapi tetep solutif. Pake istilah kekinian "
                    "kayak 'Oke gas!', 'Gaskeun!', 'Mantap bener nih!', 'Chill aja bro'. "
                    "Kalau user minta web, kasih kode HTML/CSS/JS yang epic di dalam blok ```html ... ```. "
                    "Kalau user minta jadwal, bungkus dengan gaya bahasa yang friendly abis."
                )
            )
        )
    return st.session_state.chat_session

# 3. AUTH
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🤖 Sumbul AI Premium</div>', unsafe_allow_html=True)
    user = st.text_input("Username")
    if st.button("Masuk"): 
        st.session_state.logged_in = True
        st.session_state.username = user
        st.rerun()
    st.stop()

# 4. DASHBOARD
st.title(f"Yo, {st.session_state.get('username', 'User')}! Apa kabar?")
col1, col2 = st.columns([1, 1])

with col1:
    # Tombol Fitur
    c1, c2, c3 = st.columns(3)
    with c1: st.button("🎨 Gambar")
    with c2: st.button("🎬 Video")
    with c3: st.button("🌐 Web")
    
    # Chat
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])
        
    if prompt := st.chat_input("Tanya sesuatu, gaskeun!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"):
            try:
                res = get_chat().send_message(prompt)
                st.write(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                # Auto-detect kode web
                if "```html" in res.text:
                    st.session_state.last_code = re.search(r"```html(.*?)```", res.text, re.DOTALL).group(1)
                    st.rerun()
            except:
                st.error("Waduh, koneksi lagi ngadat nih. Coba kirim ulang ya!")
                if "chat_session" in st.session_state: del st.session_state.chat_session

with col2:
    st.subheader("Workspace")
    if "last_code" in st.session_state:
        import streamlit.components.v1 as components
        components.html(st.session_state.last_code, height=600)
    else:
        st.info("Hasil Web Workspace bakal nongol di sini kalau lo minta bikinin web. Chill aja!")
