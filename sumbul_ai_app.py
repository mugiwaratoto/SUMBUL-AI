import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

st.set_page_config(page_title="Sumbul AI v2.0", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Model Flash buat chat biar super ngebut
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("🤖 Sumbul AI | Chat & Gambar")

if "messages" not in st.session_state: st.session_state.messages = []

# Fungsi buat generate gambar (Pake model Imagen)
def generate_image(prompt):
    try:
        # Imagen 3 buat generate gambar
        imagen = genai.GenerativeModel("imagen-3.0-generate-001")
        result = imagen.generate_content(prompt)
        # Mengonversi bytes ke gambar
        image = Image.open(io.BytesIO(result.candidates[0].content.parts[0].image_bytes))
        return image
    except Exception as e:
        return None

# Loop Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg: st.image(msg["image"])

if prompt := st.chat_input("Tanya atau minta gambarin sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # Cek apakah user minta gambar
        if "gambarin" in prompt.lower() or "buatkan gambar" in prompt.lower():
            with st.spinner("Lagi nge-render gambar..."):
                img = generate_image(prompt)
                if img:
                    st.image(img)
                    st.session_state.messages.append({"role": "assistant", "content": "Nih gambarnya!", "image": img})
                else:
                    st.error("Gagal buat gambar, server lagi sibuk.")
        else:
            # Chat biasa (pake Flash biar ngebut)
            res = model.generate_content(f"Jawab santai: {prompt}")
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
