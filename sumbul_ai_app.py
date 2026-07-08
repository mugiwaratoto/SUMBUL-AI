import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Sumbul AI", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key kosong di Secrets!")
    st.stop()

genai.configure(api_key=api_key)

# FUNGSI AUTO-DETECT MODEL
def get_best_model():
    # Nyari model yang support generateContent dan paling umum dipake
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # Utamakan model yang ada kata 'flash' karena paling stabil buat akun baru
            if 'flash' in m.name:
                return genai.GenerativeModel(m.name)
    # Fallback ke model pertama yang ketemu
    return genai.GenerativeModel(genai.list_models()[0].name)

st.title("🤖 Sumbul AI (Auto-Mode)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tanya apa lo? Gaskeun!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # Panggil model yang udah di-detect
            model = get_best_model()
            persona = "Lo Sumbul AI, gaya tongkrongan 2026. Santai, agak kasar, solutif."
            response = model.generate_content(f"{persona} Pertanyaan: {prompt}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.caption(f"Model yang dipake: {model.model_name}")
            
        except Exception as e:
            st.error(f"Masih error nih: {str(e)}")
