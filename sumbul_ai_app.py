import streamlit as st
import google.generativeai as genai
import time

# KONFIGURASI
st.set_page_config(page_title="Sumbul AI", layout="wide")

# Konfigurasi API
# Pastikan GEMINI_API_KEY sudah di-set di Streamlit Settings -> Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key belum di-set di Secrets Streamlit!")
    st.stop()

# LOGIKA AI STABIL
def get_ai_response(prompt):
    try:
        # Pake model flash yang lebih enteng & stabil
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Persona Tongkrongan 2026
        persona = (
            "Lo Sumbul AI, asisten tongkrongan 2026. Jawab super santai, "
            "dikit kasar (anjir/bego), dan to the point. "
        )
        response = model.generate_content(persona + prompt)
        return response.text
    except Exception as e:
        return f"Waduh, server lagi tantrum, coba lagi napa! (Error: {str(e)})"

# UI
st.title("🤖 Sumbul AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input Chat
if prompt := st.chat_input("Tanya sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Lagi mikir..."):
            res = get_ai_response(prompt)
            st.write(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
