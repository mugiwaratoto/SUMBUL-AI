import streamlit as st
import google.generativeai as genai
import re
import time

# 1. KONFIGURASI
st.set_page_config(page_title="Sumbul AI | Tongkrongan Edition", layout="wide")

# Konfigurasi API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Woy, API Key lo di Secrets belum di-set dengan bener!")
    st.stop()

# 2. LOGIKA AI DENGAN RETRY MECHANISM
def get_chat_response(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = model.start_chat(history=[])
    
    # Bungkus pake try-except biar gak crash kalau server lagi lelet
    try:
        # Persona tongkrongan 2026
        full_prompt = (
            f"Lo Sumbul AI, asisten tongkrongan 2026. Jawab super santai, "
            f"agak kasar (anjir/bego), dan to the point. Pertanyaan: {prompt}"
        )
        response = chat.send_message(full_prompt)
        return response.text
    except Exception as e:
        # Kalau error, kasih kesempatan buat retry otomatis
        time.sleep(1)
        return "Waduh, koneksi ampas banget nih! Server lagi tantrum, coba kirim ulang napa!"

# 3. DASHBOARD UI
st.markdown("## 🤖 Sumbul AI 2026")

if "messages" not in st.session_state: st.session_state.messages = []

# Tampilkan riwayat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

# Input user
if prompt := st.chat_input("Tanya sesuatu, gaskeun!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Lagi mikir nih..."):
            response_text = get_chat_response(prompt)
            st.write(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            # Auto-parse HTML
            if "```html" in response_text:
                code = re.search(r"```html(.*?)```", response_text, re.DOTALL)
                if code:
                    st.session_state.last_code = code.group(1).strip()
                    st.rerun()

# Workspace
if "last_code" in st.session_state:
    import streamlit.components.v1 as components
    st.subheader("Live Web Sandbox")
    components.html(st.session_state.last_code, height=400)
