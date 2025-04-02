import streamlit as st
import os
import time  # ajout de l'import pour simuler la lecture des PDF
import PyPDF2  # nouvel import pour extraire le texte des PDFs

from langchain.chat_models import ChatOpenAI

openai_api_key = os.environ.get("OPENAI_API_KEY")

st.title("🔎 NoteGenius - Chat with your Lessons")

# Encapsuler l'upload dans un conteneur pour pouvoir le masquer après
upload_container = st.empty()
pdf_files = upload_container.file_uploader("Chargez vos fichiers PDF de votre cours", type="pdf", accept_multiple_files=True)
if not pdf_files:
    st.warning("Veuillez charger les fichiers PDF de votre cours afin de pouvoir discuter avec le chat.")
    st.stop()
upload_container.empty()

# Traiter les PDF uniquement une fois et stocker le résultat en session_state
if "pdf_excerpt" not in st.session_state:
    with st.spinner("Lecture des fichiers PDF et préparation de la première requête..."):
        pdf_text = ""
        for pdf in pdf_files:
            reader = PyPDF2.PdfReader(pdf)
            for page in reader.pages:
                pdf_text += page.extract_text() or ""
            pdf_text += "\n"
        time.sleep(1)  # simulation supplémentaire de traitement
        st.session_state["pdf_excerpt"] = pdf_text[:4000]  # Ajuster la limite selon vos besoins

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Vous pouvez désormais poser vos questions sur le(s) cours fournis."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Remplacer l'appel st.chat_input par deux colonnes : la zone de saisie et le bouton trombone pour importer des fichiers supplémentaires
col_chat, col_file = st.columns([4, 1])
with col_chat:
    prompt = st.chat_input(placeholder="Posez votre question ici...")
with col_file:
    extra_files = st.file_uploader("📎", type="pdf", accept_multiple_files=True, key="extra_files")
    if extra_files:
        with st.spinner("Lecture des fichiers supplémentaires..."):
            extra_text = ""
            for pdf in extra_files:
                reader = PyPDF2.PdfReader(pdf)
                for page in reader.pages:
                    extra_text += page.extract_text() or ""
                extra_text += "\n"
            time.sleep(1)
            # Append text from additional files to l'extrait existant
            st.session_state["pdf_excerpt"] += extra_text[:4000]

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    llm = ChatOpenAI(model_name="GPT-4o mini", openai_api_key=openai_api_key, streaming=True)
    with st.chat_message("assistant"):
        prompt_with_context = f"Contenu des cours (extrait):\n{st.session_state['pdf_excerpt']}\nQuestion: {prompt}"
        response = llm.predict(prompt_with_context)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
