import streamlit as st
import os
import time  # ajout de l'import pour simuler la lecture des PDF
import PyPDF2  # nouvel import pour extraire le texte des PDFs

from langchain.chat_models import ChatOpenAI

st.set_page_config(page_title="NoteGenius", page_icon="📚")

openai_api_key = os.environ.get("OPENAI_API_KEY")

# Gestion des conversations multiples
if "conversations" not in st.session_state:
    st.session_state["conversations"] = {}  # Dictionnaire pour stocker les conversations
if "current_conversation" not in st.session_state:
    # Créer une première conversation par défaut si aucune n'existe
    default_conversation_name = f"Conversation {len(st.session_state['conversations']) + 1}"
    st.session_state["conversations"][default_conversation_name] = {
        "messages": [],
        "pdf_excerpt": ""
    }
    st.session_state["current_conversation"] = default_conversation_name

# Barre latérale pour gérer les conversations
with st.sidebar:
    st.title("Conversations")
    conversation_names = list(st.session_state["conversations"].keys())
    selected_conversation = st.selectbox(
        "Sélectionnez une conversation", options=conversation_names
    )

    if st.button("Nouvelle conversation"):
        new_conversation_name = f"Conversation {len(st.session_state['conversations']) + 1}"
        st.session_state["conversations"][new_conversation_name] = {
            "messages": [],
            "pdf_excerpt": ""
        }
        st.session_state["current_conversation"] = new_conversation_name
        st.experimental_rerun()

    st.session_state["current_conversation"] = selected_conversation

# Vérifier si une conversation est active
if not st.session_state["current_conversation"]:
    st.warning("Veuillez sélectionner ou créer une conversation.")
    st.stop()

# Charger la conversation active
current_conversation = st.session_state["conversations"][st.session_state["current_conversation"]]

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
        current_conversation["pdf_excerpt"] = pdf_text[:4000]  # Ajuster la limite selon vos besoins

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

    if not current_conversation.get("pdf_context_sent", False):
        prompt_with_context = f"Contenu des cours (extrait):\n{current_conversation['pdf_excerpt']}\nQuestion: {prompt}"
        current_conversation["pdf_context_sent"] = True
    else:
        prompt_with_context = prompt

    # Limiter la longueur du prompt
    max_context_length = 3500
    if len(prompt_with_context) > max_context_length:
        prompt_with_context = prompt_with_context[:max_context_length]

    llm = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key, streaming=True)
    with st.chat_message("assistant"):
        response = llm.predict(prompt_with_context)
        current_conversation["messages"].append({"role": "assistant", "content": response})
        st.write(response)
