import streamlit as st
import streamlit.components.v1 as components
import re, time
from google import genai
from google.genai import types

# --- KONFIGURASI ---
st.set_page_config(page_title="Sumbul AI OS", layout="wide")

# --- INISIALISASI SESSION STATE ---
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

# --- TOOLS & FUNGSI AI ---
def buat_pengingat(tugas, waktu): return f"✅ Agenda '{tugas}' dijadwalkan untuk '{waktu}'."
def extract_web_code(text):
    match = re.search(r"```html(.*?)```", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None

# --- AUTH GATEWAY ---
if not st.session_state.is_logged_in:
    st.title("🔐 Sumbul AI Access")
    user = st.text_input("Username")
    if st.button("Login"):
        st.session_state.is_logged_in = True
        st.session_state.username = user
        st.rerun()
    st.stop()

# --- MAIN DASHBOARD ---
st.title(f"🤖 Sumbul AI | Halo, {st.session_state.username}")
col1, col2 = st.columns([1, 1])

# LOGIKA AI
def get_chat():
    if "chat_session" not in st.session_state:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.chat_session = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction="Kamu adalah asisten serba bisa. Untuk jadwal gunakan tool 'buat_pengingat'. Untuk web, berikan kode HTML dalam blok ```html...```."
            )
        )
    return st.session_state.chat_session

with col1:
    st.subheader("Chat Assistant")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])
            
    if prompt := st.chat_input("Perintah: Buat jadwal / Buat website..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            try:
                chat = get_chat()
                response = chat.send_message(prompt)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                if code := extract_web_code(response.text):
                    st.session_state.last_code = code
                    st.rerun()
            except:
                st.error("Koneksi terputus. Silakan coba lagi.")
                if "chat_session" in st.session_state: del st.session_state.chat_session

with col2:
    st.subheader("Live Web Sandbox")
    if "last_code" in st.session_state:
        components.html(st.session_state.last_code, height=600, scrolling=True)
        if st.download_button("💾 Download HTML", st.session_state.last_code, "web.html"):
            st.success("Tersimpan!")
    else:
        st.info("Minta AI membuat website untuk melihat pratinjau di sini.")

# --- DIAGRAM ALUR KERJA SISTEM ---
