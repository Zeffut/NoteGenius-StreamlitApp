import streamlit as st

st.set_page_config(page_title="NoteGenius - Accueil", page_icon="📚")

# Gestion des conversations multiples
if "conversations" not in st.session_state:
    st.session_state["conversations"] = []  # Liste pour stocker les noms des conversations

st.title("NoteGenius - Accueil")

# Afficher la liste des conversations
st.sidebar.title("Conversations")
for conversation in st.session_state["conversations"]:
    if st.sidebar.button(conversation):
        st.experimental_set_query_params(conversation=conversation)
        st.experimental_rerun()

# Ajouter une nouvelle conversation
if st.sidebar.button("Nouvelle conversation"):
    new_conversation_name = f"Conversation {len(st.session_state['conversations']) + 1}"
    st.session_state["conversations"].append(new_conversation_name)
    st.experimental_set_query_params(conversation=new_conversation_name)
    st.experimental_rerun()

st.write("Sélectionnez ou créez une conversation dans la barre latérale.")
