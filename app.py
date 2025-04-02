import streamlit as st
import os
import time  # ajout de l'import pour simuler la lecture des PDF

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

# Ajouter un spinner pendant la lecture des PDF et la préparation de la requête initiale
with st.spinner("Lecture des fichiers PDF et préparation de la première requête..."):
    # ...traitement des PDF, par exemple extraire leur contenu...
    time.sleep(2)  # simulation de lecture et traitement

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, I'm a chatbot who can chat with the OpenAI API. How can I help you?"}
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
        response = llm.predict(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
