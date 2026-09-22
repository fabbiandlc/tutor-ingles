from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ollama_service import chat_with_ollama, check_ollama_status

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    response: str


@router.get("/health")
async def health_check():
    ollama_ok = await check_ollama_status()
    return {
        "status": "ok",
        "ollama": "connected" if ollama_ok else "disconnected",
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    ollama_ok = await check_ollama_status()
    if not ollama_ok:
        raise HTTPException(
            status_code=503,
            detail="Ollama is not running. Please start Ollama.",
        )

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    response = await chat_with_ollama(messages)
    return ChatResponse(response=response)