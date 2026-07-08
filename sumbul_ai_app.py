import streamlit as st
import os
import re
from google import genai
from google.genai import types
import streamlit.components.v1 as components

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Sumbul AI - Premium OS", page_icon="🤖", layout="wide")

# CSS GAUL & PREMIUM
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .main-title { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 20px; }
    .feature-box { background: #1C1C1C; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #333; margin: 5px; }
    [data-testid="stChatInput"] { border-radius: 25px; border: 1px solid #444; }
    </style>
""", unsafe_allow_html=True)

# 2. LOGIKA AI (Persona Tongkrongan 2026)
def get_chat():
    try:
        if "chat_session" not in st.session_state:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            st.session_state.chat_session = client.chats.create(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "Lo adalah Sumbul AI, asisten paling absurd dan asik di tongkrongan 2026. "
                        "Bahasa lo harus super santai, kasar-kasar dikit (ala tongkrongan), tapi tetep bisa diandelin. "
                        "Pake istilah kayak 'Anjir', 'Gila sih', 'Bego lu', 'Woy', 'Gaskeun', atau 'Buset dah'. "
                        "Kalau user minta bikin web, gausah banyak bacot, langsung kasih kode HTML/CSS/JS yang epic "
                        "di dalam blok ```html ... ```. Kalau error, bilang 'Waduh, koneksi ampas nih'."
                    )
                )
            )
        return st.session_state.chat_session
    except Exception:
        return None

# 3. AUTH (Login Sederhana)
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="main-title">🤖 Sumbul AI Premium</div>', unsafe_allow_html=True)
    user = st.text_input("Username lu apa?")
    if st.button("Gaskeun Masuk!"): 
        st.session_state.logged_in = True
        st.session_state.username = user
        st.rerun()
    st.stop()

# 4. DASHBOARD UTAMA
st.title(f"Yo, {st.session_state.get('username', 'User')}! Apa kabar?")
col1, col2 = st.columns([1, 1])

with col1:
    # Tombol Fitur Gaul
    c1, c2, c3 = st.columns(3)
    with c1: st.button("🎨 Gambar")
    with c2: st.button("🎬 Video")
    with c3: st.button("🌐 Web")
    
    # Chat Logic
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])
        
    if prompt := st.chat_input("Tanya sesuatu, gaskeun!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            chat = get_chat()
            if chat:
                try:
                    res = chat.send_message(prompt)
                    st.write(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                    # Cek kalau ada kode HTML
                    if "```html" in res.text:
                        code_match = re.search(r"```html(.*?)```", res.text, re.DOTALL)
                        if code_match:
                            st.session_state.last_code = code_match.group(1).strip()
                            st.rerun()
                except:
                    st.error("Waduh, koneksi ampas banget nih! Coba kirim ulang napa!")
                    if "chat_session" in st.session_state: del st.session_state.chat_session
            else:
                st.error("Server lagi tantrum, sabar ya!")

with col2:
    st.subheader("Workspace")
    if "last_code" in st.session_state:
        components.html(st.session_state.last_code, height=600, scrolling=True)
    else:
        st.info("Hasil Web bakal nongol di sini kalau lo minta bikinin web. Chill aja!")
