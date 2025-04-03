import streamlit as st
import os
import time
import PyPDF2
from langchain.chat_models import ChatOpenAI

st.set_page_config(page_title="NoteGenius", page_icon="📚")

openai_api_key = os.environ.get("OPENAI_API_KEY")

# Page principale
def main_page():
    st.title("Bienvenue sur NoteGenius")
    st.write("Chargez vos fichiers PDF pour commencer une nouvelle conversation.")

    # Zone d'importation des fichiers PDF
    pdf_files = st.file_uploader(
        "Chargez vos fichiers PDF de votre cours", type="pdf", accept_multiple_files=True
    )
    if pdf_files:
        # Utiliser le nom du premier fichier PDF comme nom de la conversation
        first_pdf_name = pdf_files[0].name
        new_conversation_name = first_pdf_name
        st.session_state["conversations"][new_conversation_name] = {
            "messages": [],
            "pdf_excerpt": ""
        }
        # Charger le contenu du premier fichier PDF
        pdf_text = ""
        reader = PyPDF2.PdfReader(pdf_files[0])
        for page in reader.pages:
            pdf_text += page.extract_text() or ""
        st.session_state["conversations"][new_conversation_name]["pdf_excerpt"] = pdf_text[:8000]
        # Rediriger vers la nouvelle conversation
        st.session_state["page"] = new_conversation_name
        st.rerun()

# Fonction pour créer une page de conversation
def create_conversation_page(conversation_name):
    st.title(f"Conversation: {conversation_name}")

    # Charger la conversation active
    current_conversation = st.session_state["conversations"][conversation_name]

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
            current_conversation["pdf_excerpt"] = pdf_text[:8000]  # Ajuster la limite selon vos besoins

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

# Ajouter une page pour créer une nouvelle conversation
def new_conversation_page():
    st.title("Nouvelle Conversation")
    st.write("Cliquez sur le bouton ci-dessous pour créer une nouvelle conversation.")
    pdf_files = st.file_uploader(
        "Chargez vos fichiers PDF de votre cours", type="pdf", accept_multiple_files=True
    )
    if pdf_files:
        # Utiliser le nom du premier fichier PDF comme nom de la conversation
        first_pdf_name = pdf_files[0].name if pdf_files else f"Conversation {len(st.session_state['conversations']) + 1}"
        new_conversation_name = first_pdf_name
        st.session_state["conversations"][new_conversation_name] = {
            "messages": [],
            "pdf_excerpt": ""
        }
        # Charger le contenu du premier fichier PDF
        pdf_text = ""
        reader = PyPDF2.PdfReader(pdf_files[0])
        for page in reader.pages:
            pdf_text += page.extract_text() or ""
        st.session_state["conversations"][new_conversation_name]["pdf_excerpt"] = pdf_text[:8000]
        st.rerun()

# Initialiser les conversations dans l'état de session
if "conversations" not in st.session_state:
    st.session_state["conversations"] = {}

# Créer une page pour chaque conversation avec un nom unique
pages = [new_conversation_page]
for conversation_name in st.session_state["conversations"].keys():
    def generate_page(name):
        def page():
            create_conversation_page(name)
        page.__name__ = name  # Attribuer un nom unique à la fonction
        return page
    a = generate_page(conversation_name)
    pages.append(a)
    st.switch_page(st.Page(a))

# Afficher la page principale si aucune navigation n'est active
if "page" not in st.session_state:
    main_page()
else:
    # Configuration de la navigation
    pg = st.navigation(pages)
    pg.run()
