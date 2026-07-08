import streamlit as st
import google.generativeai as genai

# Konfigurasi halaman
st.set_page_config(page_title="Sumbul AI", page_icon="🤖")

# Ambil API Key dari Secrets Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key belum di-set di Streamlit Secrets!")
    st.stop()

# Konfigurasi Google GenAI
genai.configure(api_key=api_key)

# Pake model 'gemini-1.5-pro' yang lebih stabil untuk project baru
model = genai.GenerativeModel("gemini-1.5-pro")

st.title("🤖 Sumbul AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanya sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Kirim pesan dengan persona santai
            response = model.generate_content(
                f"Lo adalah Sumbul AI, gaya tongkrongan 2026. Santai, agak kasar, solutif. Pertanyaan: {prompt}"
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.write("Coba cek di Google AI Studio kalau model ini masih belum ke-enable di project lo.")
