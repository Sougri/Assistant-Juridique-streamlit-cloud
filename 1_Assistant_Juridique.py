import nest_asyncio
nest_asyncio.apply()

from utility import *

import streamlit as st
import os
from streamlit.runtime.scriptrunner import get_script_run_ctx ### Pour obtenir l'ID de session
from supabase import create_client, Client

# --- Initialisation du client Supabase ---
# À placer au début de votre script, après les imports
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# On ne crée le client que si les clés sont bien présentes
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Client Supabase initialisé avec succès.")
else:
    print("Attention : Clés Supabase non trouvées. Les logs ne seront pas sauvegardés.")

# --- Configuration de la page et des styles ---
st.set_page_config(page_title="Assistant Juridique", page_icon="⚖️")

# --- Interface utilisateur Streamlit ---

st.title("⚖️ Assistant Juridique")
st.markdown('<div style="text-align: justify;">Le Code pénal et le Code de procédure pénale du Burkina Faso constituent les fondements du système répressif national. Le premier établit les infractions (crimes, délits, contraventions) ainsi que les peines correspondantes ; le second encadre les règles relatives aux enquêtes, aux poursuites et au jugement des infractions.</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: justify;">Dans le cadre de ce projet, ces deux textes servent de base documentaire à une chabot intelligent conçue pour faciliter l’accès à l’information juridique. L’objectif est de permettre aux utilisateurs juristes ou non d’interroger ces textes à travers question simple ou complexe, tout en garantissant des réponses fiables, contextualisées et conformes à la législation en vigueur.</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: justify;">NB: Il est important de noter que l’application ne couvre que les thématiques relevant du droit pénal et de la procédure pénale, et n’inclut pas d’autres branches du droit, telles que le droit de la famille, le droit civil ou le droit commercial.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

st.sidebar.title("Gerer l'Assistant")
if st.sidebar.button("Réinitialiser la Conversation", type="primary"):
    # Vérifier si la mémoire et les messages existent avant de les effacer
    if "memory" in st.session_state:
        del st.session_state.memory
    if "messages" in st.session_state:
        del st.session_state.messages
    # Forcer le rechargement de la page pour que la chaîne et l'affichage soient bien réinitialisés
    st.rerun()

# Charger la chaîne conversationnelle pour la session actuelle
chain = get_conversational_chain()

# POINT CLÉ N°2 : Initialisation de l'historique des messages propre à la session
# De même que pour la mémoire, 'messages' est créé une fois par session
# pour stocker et afficher l'historique du chat.
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Afficher les messages de l'historique de la session en cours
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Gérer la nouvelle entrée de l'utilisateur
if user_prompt := st.chat_input("Posez votre question ici..."):
    # Ajouter et afficher le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Obtenir la réponse de l'assistant
    with st.spinner("L'assistant réfléchit..."):
        result = chain({"question": user_prompt})
        response = result["answer"]
        
        ### MODIFICATION N°2 : Extraire, formater et logger le contexte ###
        # Le résultat contient maintenant une clé 'source_documents'
        retrieved_context = ""
        if 'source_documents' in result and result['source_documents']:
            # Formater chaque morceau de contexte pour une lecture facile
            formatted_docs = []
            for i, doc in enumerate(result['source_documents']):
                # Nettoyer le contenu pour qu'il tienne sur une seule ligne de log
                clean_content = doc.page_content.replace('\n', ' ').replace('"', "'")
                source_info = doc.metadata.get('source', 'N/A')
                formatted_docs.append(f"[CHUNK {i+1} | Source: {source_info}] > \"{clean_content}\"")
            
            # Joindre tous les morceaux formatés en une seule chaîne
            retrieved_context = " | ".join(formatted_docs)

        # Préparer les données à insérer dans la base de données
        log_data = {
            "session_id": get_script_run_ctx().session_id,
            "user_question": user_prompt,
            "retrieved_context": retrieved_context,
            "assistant_response": response
        }

        # Envoyer les données à Supabase (si le client est initialisé)
        if supabase:
            try:
                supabase.table("logs").insert(log_data).execute()
            except Exception as e:
                # Afficher une erreur dans la console si l'envoi échoue
                print(f"Erreur lors de l'envoi du log à Supabase : {e}")

        
        # Ajouter et afficher la réponse de l'assistant
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
