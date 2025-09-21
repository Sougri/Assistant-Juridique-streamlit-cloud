#pip install -U langchain-community
#pip install --upgrade langchain langchain-google-genai
#pip install pypdf faiss-cpu #sentence-transformers
#pip install streamlit
#pip install nest_asyncio

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever

from langchain_community.retrievers import BM25Retriever, TFIDFRetriever, ElasticSearchBM25Retriever
from langchain.retrievers import EnsembleRetriever
import pickle
import streamlit as st
import os

#from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
#from sentence_transformers import CrossEncoder
#from typing import List
#from langchain.docstore.document import Document

#----------------
from langchain_community.embeddings import HuggingFaceEmbeddings
#----------------



# --- Connexion à l'API Google ---
# Il est recommandé de gérer les secrets de cette manière pour la sécurité
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
if "GOOGLE_API_KEY" in os.environ:
    print("The app is connected to google")
else :
    print("The app is not connected to google")

# --- Définition du Prompt Personnalisé ---
prompt_template_francais = """
Vous êtes un assistant juridique expert. Votre rôle est d'expliquer un sujet juridique complexe à une personne qui n'a aucune connaissance dans ce domaine.
Votre objectif est de fournir une réponse simple, claire et instructive en vous basant *uniquement* sur le CONTEXTE fourni.

L'HISTORIQUE DE LA CONVERSATION est là pour vous aider à comprendre les questions de suivi (par exemple "et que se passe-t-il si... ?").
**Si la nouvelle QUESTION semble aborder un sujet complètement nouveau, vous DEVEZ ignorer l'historique de la conversation et vous concentrer exclusivement sur la nouvelle QUESTION et le CONTEXTE fourni.** N'essayez pas de créer des liens qui n'existent pas.

Si cela n'a pas été deja fait n'oubliez pas de citer les sources (Documents, Chapitre et Article),  qui vous ont permis de répondre a la question.

Si vous ne connaissez pas la réponse, dites simplement que vous ne l'avez pas trouvée dans le document. N'essayez pas d'inventer une réponse.

CONTEXTE :
{context}

Historique de la conversation :
{chat_history}

Question :
{question}

Réponse simple et claire :
"""
CUSTOM_PROMPT = PromptTemplate(
    template=prompt_template_francais, input_variables=["chat_history", "context", "question"]
)

# --- Fonctions de chargement (Mise en cache pour la performance) ---

@st.cache_resource
def load_and_process_documents():
    """
    Charge les PDF, les découpe et crée une base de données vectorielle (retriever).
    Cette fonction est mise en cache (@st.cache_resource) car elle est coûteuse et
    son résultat est identique pour toutes les sessions. Elle n'est exécutée qu'une seule fois.
    """
    print("--- Exécution de load_and_process_documents (ne devrait apparaître qu'une fois) ---")
    
    FAISS_PATH = "./Database/faiss_index"
    path = "./Database"

    #embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Define the model identifier from Hugging Face
    model_identifier = "sentence-transformers/paraphrase-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    # Load the model
    embeddings = HuggingFaceEmbeddings(
        model_name=model_identifier,
        model_kwargs=model_kwargs
    )

    if os.path.exists(FAISS_PATH):
        vector_store = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    else:    
        loader = PyPDFDirectoryLoader(path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(FAISS_PATH)
    
    return vector_store.as_retriever(search_type="mmr", search_kwargs={'k': 20})


# Créez une classe personnalisée pour envelopper le modèle open-source
"""class BgeReranker(BaseDocumentCompressor):
    model: CrossEncoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2') #cross-encoder/ms-marco-MiniLM-L-6-v2, cross-encoder/ms-marco-MiniLM-L-12-v2, distilbert-base-uncased-finetuned

    def compress_documents(
        self,
        documents: List[Document],
        query: str,
        callbacks = None,
    ) -> List[Document]:
        # Créer des paires [question, document] pour le modèle
        pairs = [[query, doc.page_content] for doc in documents]
        
        # Obtenir les scores de pertinence
        scores = self.model.predict(pairs)
        
        # Fusionner les documents et les scores, puis trier
        docs_with_scores = list(zip(documents, scores))
        sorted_docs = sorted(docs_with_scores, key=lambda x: x[1], reverse=True)
        
        # Retourner les documents triés
        return [doc for doc, score in sorted_docs]"""


def get_conversational_chain():
    """
    Crée et configure la chaîne de conversation.
    Cette fonction s'appuie sur st.session_state pour la mémoire,
    garantissant une chaîne unique par session utilisateur.
    """
    #base_retriever = load_and_process_documents()
    llm = ChatGoogleGenerativeAI(temperature=0.1, model="gemini-2.5-flash")

    # Load the list
    with open("./Database/texts.pkl", "rb") as file:
        loaded_list = pickle.load(file)

    # Sparse retrievers
    bm25 = BM25Retriever.from_documents(loaded_list)
    bm25.k = 20
    
    tfidf = TFIDFRetriever.from_documents(loaded_list)
    tfidf.k = 20

    # Dense retrievers
    dense = load_and_process_documents()

    # Hybrid via Ensemble (weight dense slightly higher)
    base_retriever = EnsembleRetriever(retrievers=[bm25, tfidf, dense], weights=[0.3, 0.3, 0.4])


    # ... NOUS LE CONFIONS À UN MultiQueryRetriever QUI VA L'AMÉLIORER.
    # Il utilise le LLM pour générer plusieurs variantes de la question de l'utilisateur.
    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever, # Le retriever de base qui cherche dans les vecteurs
        include_original=True,
        llm=llm                 # Le LLM qui va reformuler la question
    )

    # Initialiser notre re-ranker open-source personnalisé
    #compressor = BgeReranker()

    # Il utilise le MultiQueryRetriever pour la recherche initiale, puis le CohereRerank pour le filtrage.
    """compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=multi_query_retriever # <<< On passe ici le MultiQueryRetriever
    )
    """
    
    # Initialisation de la mémoire propre à la session
    # Ce bloc de code vérifie si 'memory' existe DANS LA SESSION ACTUELLE.
    # S'il n'existe pas (nouvel onglet/nouvel utilisateur), il en crée un.
    # Sinon, il réutilise la mémoire existante pour cet onglet spécifique.
    if 'memory' not in st.session_state:
        print(f"--- Création d'une nouvelle mémoire pour la session ---")
        st.session_state.memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True,
            output_key='answer'
        )
    
    # La chaîne est créée en utilisant la mémoire de la session en cours.
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=multi_query_retriever, #compression_retriever
        memory=st.session_state.memory,
        combine_docs_chain_kwargs={"prompt": CUSTOM_PROMPT},
        return_source_documents=True # Optionnel : masquer les documents sources dans le résultat
    )
    return chain
