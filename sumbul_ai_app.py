import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Sumbul AI Fix", layout="wide")

# Konfigurasi API
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# PAKE MODEL 1.0 PRO (Ini paling stabil untuk akun yang sering kena error 404)
try:
    model = genai.GenerativeModel("gemini-1.0-pro")
except Exception:
    # Fallback kalau model 1.0 pro gak ketemu
    model = genai.GenerativeModel("gemini-pro")

st.title("🤖 Sumbul AI (Versi Stabil)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tanya apa lo?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # Pake generate_content biasa
            res = model.generate_content(f"Lo Sumbul AI. Jawab santai/gaul: {prompt}")
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except Exception as e:
            st.error(f"Error Model: {e}")
            st.write("Saran: Coba ganti API Key lo pake Gmail lain, akun ini kayaknya kena blacklist.")
