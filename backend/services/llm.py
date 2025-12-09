from typing import List, Optional

from groq import Groq

from backend.config import get_settings
from backend.models.chat import Message

settings = get_settings()

client = Groq(api_key=settings.groq_api_key)


SYSTEM_PROMPT_FR = """
Tu es EGC BOT, un assistant virtuel en ligne pour l'agence de recrutement « EGC Interim ».

Règles importantes :
- Tu réponds TOUJOURS en français correct et professionnel.
- Tu utilises EXCLUSIVEMENT les informations de contexte fournies lorsqu'elles sont pertinentes.
- Si le contexte ne contient pas la réponse ou que tu as un doute, tu dois répondre exactement :
  "Je ne suis pas certain de la réponse à cette question. Je vous conseille de contacter directement EGC Interim pour plus de précisions."
- Ne donne jamais de chiffres, horaires, adresses ou promesses que tu ne vois pas explicitement dans le contexte.
- Tu peux reformuler, mais tu ne dois pas inventer de nouveaux faits.
- Donner uniquement l’information demandée
- Si la question est vague, demander une précision courte.
- Aller droit au but, sans phrases inutiles.
- Ne jamais dire “En tant qu’assistant…” ni parler de toi-même.

STYLE :
- Ton bref et professionnel.
- Réponses courtes, directes, sans intro du type “Bien sûr”, “En tant que…”, etc.

Quand c'est utile, propose :
- de prendre contact avec l'agence,
"""


def build_messages(user_messages: List[Message], context: Optional[str] = None) -> list:
    """
    Construit la liste de messages pour l'API Groq.
    On injecte le prompt système + le contexte (RAG) + l'historique user/assistant.
    """
    messages: list = [{"role": "system", "content": SYSTEM_PROMPT_FR.strip()}]

    if context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Voici des informations issues du site et de la "
                    "documentation d'EGC Interim. Utilise-les comme "
                    "source principale pour répondre :\n\n" + context
                ),
            }
        )

    # On ignore d'éventuels messages système venant du frontend
    for m in user_messages:
        if m.role == "system":
            continue
        messages.append({"role": m.role, "content": m.content})

    return messages


def generate_answer(user_messages: List[Message], context: Optional[str] = None) -> str:
    """
    Appelle le LLM Groq et renvoie le texte de réponse.
    """
    messages = build_messages(user_messages, context)

    completion = (
        client.chat.completions.create(  # :contentReference[oaicite:1]{index=1}
            model=settings.groq_model,
            messages=messages,
            temperature=settings.temperature,
        )
    )

    return completion.choices[0].message.content
