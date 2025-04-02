import streamlit as st
import openai
import os

# Configurez votre clé API OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    st.error("Clé API OpenAI non définie. Veuillez la définir dans la variable d'environnement OPENAI_API_KEY.")
    st.stop()

st.title("Chat IA avec OpenAI")

# Initialiser l'historique de conversation dans session_state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Vous êtes un assistant IA."}
    ]

# Zone de texte pour entrer le message de l'utilisateur
user_input = st.text_input("Votre message :", key="input")

if st.button("Envoyer") and user_input:
    # Ajout du message utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Appel à l'API OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content.strip()
        # Ajout de la réponse dans l'historique
        st.session_state.messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"Erreur lors de la communication avec l'API OpenAI : {e}")

# Afficher l'historique de la conversation
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"**Vous :** {message['content']}")
    elif message["role"] == "assistant":
        st.markdown(f"**Assistant :** {message['content']}")