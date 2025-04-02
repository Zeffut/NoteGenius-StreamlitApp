import streamlit as st
import os
import time
import PyPDF2
from langchain.chat_models import ChatOpenAI

st.set_page_config(page_title="NoteGenius - Conversation", page_icon="📚")

openai_api_key = os.environ.get("OPENAI_API_KEY")

# Récupérer le nom de la conversation depuis les paramètres de l'URL
query_params = st.experimental_get_query_params()
conversation_name = query_params.get("conversation", [None])[0]

if not conversation_name:
    st.error("Aucune conversation sélectionnée. Retournez à l'accueil.")
    st.stop()

# Charger ou initialiser la conversation
if "conversations_data" not in st.session_state:
    st.session_state["conversations_data"] = {}

if conversation_name not in st.session_state["conversations_data"]:
    st.session_state["conversations_data"][conversation_name] = {
        "messages": [],
        "pdf_excerpt": ""
    }

current_conversation = st.session_state["conversations_data"][conversation_name]

st.title(conversation_name)

# Gestion des fichiers PDF pour la conversation active
if not current_conversation["pdf_excerpt"]:
    upload_container = st.empty()
    pdf_files = upload_container.file_uploader(
        "Chargez vos fichiers PDF de votre cours", type="pdf", accept_multiple_files=True
    )
    if not pdf_files:
        st.warning("Veuillez charger les fichiers PDF de votre cours pour cette conversation.")
        st.stop()
    upload_container.empty()

    with st.spinner("Lecture des fichiers PDF et préparation de la première requête..."):
        pdf_text = ""
        for pdf in pdf_files:
            reader = PyPDF2.PdfReader(pdf)
            for page in reader.pages:
                pdf_text += page.extract_text() or ""
            pdf_text += "\n"
        time.sleep(1)
        current_conversation["pdf_excerpt"] = pdf_text[:8000]

# Initialiser les messages pour la conversation active
if "messages" not in current_conversation or not current_conversation["messages"]:
    current_conversation["messages"] = [
        {"role": "assistant", "content": "Vous pouvez désormais poser vos questions sur le(s) cours fournis."}
    ]

# Afficher les messages de la conversation active
for msg in current_conversation["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Zone de saisie pour poser des questions
prompt = st.chat_input(placeholder="Posez votre question ici...")

if prompt:
    current_conversation["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # Construire le contexte de la conversation en incluant les documents et les messages précédents
    conversation_context = f"Contenu des cours (extrait):\n{current_conversation['pdf_excerpt']}\n\n"
    for message in current_conversation["messages"]:
        role = "Utilisateur" if message["role"] == "user" else "Assistant"
        conversation_context += f"{role}: {message['content']}\n"

    # Ajouter le nouveau message utilisateur au contexte
    prompt_with_context = f"{conversation_context}Utilisateur: {prompt}\nAssistant:"

    # Limiter la longueur du prompt pour éviter les erreurs
    max_context_length = 138000
    if len(prompt_with_context) > max_context_length:
        prompt_with_context = prompt_with_context[-max_context_length:]

    llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key, streaming=True)
    with st.chat_message("assistant"):
        response = llm.predict(prompt_with_context)
        current_conversation["messages"].append({"role": "assistant", "content": response})
        st.write(response)
