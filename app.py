from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import json
import time
from streamlit_pdf_viewer import pdf_viewer

from src.pdf_loader import load_pdf
from src.text_splitter import split_text
from src.embeddings import create_embeddings, model
from src.vector_store import create_faiss_index, save_index, load_index, search
from src.llm import ask_llm

# -------- PAGE CONFIG --------
st.set_page_config(page_title="AI PDF Chat", page_icon="📄", layout="wide")

# -------- SIDEBAR --------
st.sidebar.title("📂 PDF Manager")

uploaded = st.sidebar.file_uploader("Upload PDF", type="pdf")

if uploaded:

    # read file only once and store in session
    if "file_bytes" not in st.session_state:
        st.session_state.file_bytes = uploaded.read()
        st.session_state.file_name = uploaded.name

    file_bytes = st.session_state.file_bytes

    # preview PDF
    pdf_viewer(file_bytes, height=500)

    # save only if not already saved
    os.makedirs("data/uploads", exist_ok=True)
    file_path = f"data/uploads/{st.session_state.file_name}"

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "wb") as f:
            f.write(file_bytes)

    st.sidebar.success(f"Loaded: {st.session_state.file_name}")

    st.sidebar.success(f"Loaded: {uploaded.name}")

    if st.sidebar.button("Process PDF"):
        docs = load_pdf(file_path)

        chunks = []
        pages = []

        for d in docs:
            split_chunks = split_text(d["text"])
            chunks.extend(split_chunks)
            pages.extend([d["page"]] * len(split_chunks))

        vectors = create_embeddings(chunks)

        index = create_faiss_index(vectors)
        save_index(index, (chunks, pages))

        st.sidebar.success("PDF processed!")

# -------- MAIN UI --------
st.title("📄 AI Chat with Your PDFs")
st.caption("Upload a PDF from sidebar and start chatting")

# -------- CLEAR CHAT --------
if st.button("🧹 Clear Chat"):
    st.session_state.messages = []

# -------- SESSION STATE --------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------- SHOW CHAT --------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------- CHAT INPUT --------
prompt = st.chat_input("Ask something from your PDF")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        index, data = load_index()
        chunks, pages = data

        q_vector = model.encode([prompt])[0]
        results = search(index, q_vector)

        selected_chunks = [chunks[i] for i in results]
        context = "\n".join(selected_chunks)

        answer = ask_llm(context, prompt)

        highlight = selected_chunks[0][:300] if selected_chunks else ""
        answer += f"\n\n📌 **Relevant excerpt from PDF:**\n\n> {highlight}"

    except Exception as e:
        answer = f"Upload and process a PDF first.\n\nError: {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})

    # typing animation
    with st.chat_message("assistant"):
        placeholder = st.empty()
        typed = ""

        for char in answer:
            typed += char
            placeholder.markdown(typed)
            time.sleep(0.01)

# -------- DOWNLOAD CHAT --------
if st.session_state.messages:
    chat_json = json.dumps(st.session_state.messages, indent=2)

    st.download_button(
        label="📥 Download Chat History",
        data=chat_json,
        file_name="chat_history.json",
        mime="application/json"
    )