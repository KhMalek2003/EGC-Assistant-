# Chatbot EGC Interim (FR)

Chatbot d'assistance client pour **EGC Interim**, basé sur un LLM Groq + RAG (Recherche dans la documentation de l'entreprise).

## Fonctionnalités

- Dialogue en **français** uniquement.
- Utilisation du LLM Groq (`llama-3.3-70b-versatile`) pour la génération de texte.
- RAG : recherche dans les documents internes (dossier `data/source_docs`) pour répondre avec la connaissance d'EGC Interim.
- Frontend léger (HTML/CSS/JS) intégrable dans n'importe quel site (widget).

## Structure du projet

```text
backend/      # API FastAPI (Python)
frontend/     # Widget de chat (HTML/CSS/JS)
data/         # Données pour le RAG (source + index)
