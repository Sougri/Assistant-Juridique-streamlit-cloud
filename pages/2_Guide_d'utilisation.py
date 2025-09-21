import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Guide d'Utilisation", page_icon="💡")

# Titre principal
st.title("Guide d'Utilisation de l'Assistant d'Analyse")
st.markdown("---")

# Section 1 : Mission de l'outil
st.header("Objectifs")
st.info("""
L’objectif principal de cette application est de rendre le droit pénal et la procédure pénale du Burkina Faso plus accessibles, compréhensibles et exploitables par un large public, qu’il soit ou non spécialiste du domaine juridique. Elle vise à offrir un accès rapide, fiable et structuré aux dispositions pertinentes du Code pénal et du Code de procédure pénale en garantissant des réponses précises et conformes aux textes officiels. Elle permet de: 

- **Localiser** avec précision des informations spécifiques dans les document.
- **Synthétiser** des ensembles d'informations complexes.
- **Mettre en corrélation** des éléments d'information dispersés à travers différentes pages des documents.


L’application doit faciliter la compréhension des règles juridiques tout en conservant la rigueur nécessaire à l’interprétation du droit. Elle constitue ainsi un outil d’aide à la consultation pour les cadres, étudiants, praticiens du droit, institutions et citoyens, dans le strict respect du périmètre légal défini.
""")

st.markdown("---")

# Section 2 : Principes pour une interrogation efficace
st.header("Principes pour une Interrogation Efficace")
st.markdown("""
La pertinence des résultats est directement liée à la précision des requêtes. Veuillez observer les principes suivants pour une utilisation optimale.
""")

st.subheader("1. Spécificité de la Requête")
st.markdown("""
Les questions générales produiront des résultats étendus et potentiellement peu pertinents. Privilégiez des requêtes ciblées.
- **Requête à éviter :** "Peine mineur"
- **Requête recommandée :** "Quelle est la peine prévue pour un mineur ayant commis un délit ? "
""")

st.subheader("2. Utilisation de la Terminologie des document")
st.markdown("""
L’assistant identifie les informations sur la base des termes présents dans les documents. L’emploi de la terminologie correcte ou de synonymes facilite l’extraction de l’information, en permettant au système de faire correspondre plus efficacement la question de l’utilisateur aux formulations juridiques officielles, tout en assurant que la réponse soit formulée conformément aux textes de loi et compréhensible par un public non spécialiste.
""")

st.subheader("3. Exploitation des Requêtes Séquentielles")
st.markdown("""
L'Application conserve le contexte de la conversation en cours. Utilisez cette capacité pour affiner votre recherche de manière progressive.
""")

st.markdown("---")

# Section 3 : Limites fonctionnelles et avertissement
st.header("Limites Fonctionnelles et Avertissement Légal")

st.error("""
**Avertissement Fondamental : Cet outil ne se substitue en aucun cas à l'expertise d'un professionnel du droit.**

Il doit être utilsé exclusivement pour **faciliter la consultation et la compréhension du code penale**. La responsabilité de l'interprétation des informations, de la vérification de leur exactitude et des décisions qui en découlent incombe entièrement à l'utilisateur.
""")

st.warning("""
**Cadre de Connaissance Strictement Limité :**

La connaissance de l'assistant est **strictement et exclusivement délimitée au corpus documentaire qui lui est fourni**. Il n'a aucune connaissance de la législation externe, de la jurisprudence, ou de tout fait non consigné dans les documents. Il ne peut donc pas valider la conformité juridique d'une procédure ni offrir de conseil.
""")
