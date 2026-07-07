import streamlit as st
import streamlit.components.v1 as components
import re
from google import genai
from google.genai import types

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Sumbul AI - Integrated Sandbox", layout="wide")

# 2. FUNGSI SANDBOX (Mesin Render Instan)
def render_sandbox(html_code):
    """Fungsi untuk merender preview website hasil AI"""
    components.html(html_code, height=600, scrolling=True)

# 3. FUNGSI PARSING KODE WEB
def extract_web_code(text):
    """Mendeteksi kode HTML dalam respons AI"""
    match = re.search(r"```html(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

# 4. INISIALISASI AI
if "chat_session" not in st.session_state:
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.chat_session = client.chats.create(
            model="gemini-2.5-pro",
            config=types.GenerateContentConfig(
                system_instruction="Kamu adalah Web Architect. Jika diminta membuat web, berikan kode HTML lengkap (termasuk CSS/JS di dalamnya) di dalam blok ```html ... ```."
            )
        )
    except Exception as e:
        st.error(f"Error API Key: {e}")

# 5. ANTARMUKA (LAYOUT DUAL-PANE)
st.title("🤖 Sumbul AI x Integrated Web Sandbox")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Percakapan")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    # Menampilkan riwayat chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Input dari user
    if prompt := st.chat_input("Contoh: Buat halaman landing page toko baju yang keren..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("AI sedang merancang website..."):
                response = st.session_state.chat_session.send_message(prompt)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                # Parsing otomatis
                code = extract_web_code(response.text)
                if code:
                    st.session_state.last_code = code
                    st.success("Website terdeteksi! Mengeksekusi sandbox...")
                    st.rerun()

with col2:
    st.subheader("Live Sandbox Preview")
    if "last_code" in st.session_state and st.session_state.last_code:
        render_sandbox(st.session_state.last_code)
        
        # Fitur download
        st.download_button(
            label="💾 Unduh Hasil Website",
            data=st.session_state.last_code,
            file_name="hasil_karya_sumbul.html",
            mime="text/html"
        )
    else:
        st.info("Hasil website akan muncul di sini setelah Anda meminta AI membuatnya.")
