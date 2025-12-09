from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.models.chat import ChatRequest, ChatResponse
from backend.services.llm import generate_answer
from backend.services.rag import retrieve_relevant_chunks

app = FastAPI(title="EGC Interim Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    user_messages = [m for m in payload.messages if m.role == "user"]
    last_user_message = user_messages[-1] if user_messages else None

    context_text = ""
    if settings.rag_enabled and last_user_message is not None:
        chunks = retrieve_relevant_chunks(
            query=last_user_message.content,
            top_k=settings.top_k,
        )
        if chunks:
            context_text = "\n\n---\n\n".join(chunks)

    reply = generate_answer(payload.messages, context_text)

    return ChatResponse(reply=reply)
