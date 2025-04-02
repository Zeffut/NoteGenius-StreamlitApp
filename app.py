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
# Masquer la zone d'upload une fois les fichiers importés
upload_container.empty()

# Préparer une variable pour contenir le texte extrait des PDFs
pdf_text = ""
# Ajouter un spinner pendant la lecture des PDF et la préparation de la requête initiale
with st.spinner("Lecture des fichiers PDF et préparation de la première requête..."):
    for pdf in pdf_files:
        reader = PyPDF2.PdfReader(pdf)
        for page in reader.pages:
            pdf_text += page.extract_text() or ""
        pdf_text += "\n"
    time.sleep(1)  # simulation supplémentaire de traitement
    # Limiter le texte pour éviter un prompt trop volumineux
    pdf_excerpt = pdf_text[:4000]  # Ajuster la limite selon vos besoins

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Vous pouvez désormais poser vos questions sur le(s) cours fournis."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Posez votre question ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True)
    with st.chat_message("assistant"):
        # Utiliser pdf_excerpt pour fournir le contexte à l'IA
        prompt_with_context = f"Contenu des cours (extrait):\n{pdf_excerpt}\nQuestion: {prompt}"
        response = llm.predict(prompt_with_context)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)

