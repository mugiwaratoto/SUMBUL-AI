import streamlit as st
import google.generativeai as genai

# 1. SETUP HALAMAN
st.set_page_config(page_title="Sumbul AI Pro", layout="wide")

# 2. KONFIGURASI API (Wajib ambil dari Secrets)
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key lo nggak ketemu di Secrets. Setting dulu woy!")
    st.stop()

genai.configure(api_key=api_key)

# 3. SET MODEL KE 1.5 PRO
# Nama model yang benar dan standar untuk akses API
model = genai.GenerativeModel("gemini-1.5-pro")

st.title("🤖 Sumbul AI | Pro Edition")

# 4. LOGIKA CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input User
if prompt := st.chat_input("Tanya apa lo? Gaskeun!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # Kirim request ke model 1.5 Pro
            persona = "Lo Sumbul AI, gaya tongkrongan 2026. Santai, agak kasar, solutif."
            response = model.generate_content(f"{persona} Pertanyaan: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Waduh, koneksi ampas/model error: {str(e)}")
            st.write("Cek lagi di AI Studio kalau model 1.5 Pro lo udah bener-bener aktif.")
