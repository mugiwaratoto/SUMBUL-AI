import streamlit as st
import google.generativeai as genai
import re

# 1. KONFIGURASI
st.set_page_config(page_title="Sumbul AI | Tongkrongan Edition", layout="wide")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 2. LOGIKA AI (Persona Tongkrongan 2026)
def get_chat():
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Persona yang lebih 'ngegas'
        chat = model.start_chat(history=[])
        return chat
    except Exception as e:
        st.error(f"Waduh, koneksi ampas nih! {e}")
        return None

# 3. DASHBOARD
st.markdown("## 🤖 Sumbul AI | Halo, " + st.session_state.get('username', 'Ajis'))

if "messages" not in st.session_state: st.session_state.messages = []

# Sidebar/Aksi Cepat
st.sidebar.markdown("### 🎛️ Panel Quick Action")
if st.sidebar.button("🎨 Gambar"): st.info("Gaskeun, lagi gue buatin...")
if st.sidebar.button("🌐 Web"): st.info("Sabar, lagi gue coding...")

# Chat UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.write(msg["content"])

if prompt := st.chat_input("Tanya sesuatu, gaskeun!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)
    
    with st.chat_message("assistant"):
        chat = get_chat()
        if chat:
            try:
                # Instruksi Persona (Ngegas & Gaul)
                full_prompt = f"Lo asisten tongkrongan 2026. Jawab super santai, dikit kasar (anjing/anjir/bego), dan to the point. Ini pertanyaan user: {prompt}"
                res = chat.send_message(full_prompt)
                st.write(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                
                # Auto-parse HTML
                if "```html" in res.text:
                    st.session_state.last_code = re.search(r"```html(.*?)```", res.text, re.DOTALL).group(1)
                    st.rerun()
            except:
                st.error("Waduh, koneksi ampas banget nih! Coba kirim ulang napa!")
        else:
            st.error("Server lagi tantrum, sabar ya!")

# Workspace
st.subheader("Live Web Sandbox")
if "last_code" in st.session_state:
    import streamlit.components.v1 as components
    components.html(st.session_state.last_code, height=400)
else:
    st.info("Minta AI membuat website untuk melihat pratinjau di sini.")
