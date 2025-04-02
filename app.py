import streamlit as st
import os

from langchain.chat_models import ChatOpenAI

openai_api_key = os.environ.get("OPENAI_API_KEY")

st.title("🔎 NoteGenius - Chat with your Lessons")

# Ajouter l'upload des fichiers PDF de cours
pdf_files = st.file_uploader("Chargez vos fichiers PDF de votre cours", type="pdf", accept_multiple_files=True)
if not pdf_files:
    st.warning("Veuillez charger les fichiers PDF de votre cours afin de pouvoir discuter avec le chat.")
    st.stop()

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
