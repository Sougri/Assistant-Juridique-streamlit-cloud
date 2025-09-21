# ⚖️ Assistant Juridique – Burkina Faso

An intelligent chatbot designed to answer legal questions based on the **Code pénal** and **Code de procédure pénale** of Burkina Faso.  
It uses **Retrieval-Augmented Generation (RAG)** to provide accurate, contextual, and legally grounded responses.

---

## 📜 Description

The **Assistant Juridique** allows users to query Burkina Faso’s penal code and criminal procedure code using natural language.  
It returns answers supported by relevant excerpts from the law, making legal information accessible to both professionals and the general public.

> **Note:** This app only covers topics related to *droit pénal* and *procédure pénale*.  
It does **not** address other areas of law (family, civil, commercial, etc.).

---

## 🛠 Features

- **Interactive chatbot** with [Streamlit](https://streamlit.io/)  
- **Context retrieval** from official legal texts (RAG pipeline)  
- **Source display** for legal verification  
- **Conversation memory** for multi-turn interactions  
- **Usage logging to Supabase** (session ID, question, context, answer)  

---

## 🚀 Tech Stack

- **UI:** Streamlit  
- **Backend:** LangChain Conversational Retrieval Chain  
- **Database:** Supabase (for logs)  
- **Deployment:** Compatible with Render, Streamlit Cloud, etc.
