from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.mirai_agents.speaking_agent import FriendlyAgent  # agent that reads the key from .env

router = APIRouter(prefix="/mirai_agents", tags=["mirai_agents"])

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    model_name: str = Field("gemini-1.5-flash")
    temperature: float = Field(0.4, ge=0.0, le=1.0)
    context_sql: Optional[str] = Field(None, description="Additional SQL context (optional)")

class AskResponse(BaseModel):
    answer: str

@router.post("/natural/ask", response_model=AskResponse, status_code=status.HTTP_200_OK)
def ask_natural(req: AskRequest):
    try:
        agent = FriendlyAgent(model_name=req.model_name, temperature=req.temperature)
        answer = agent.respond(req.question, context_sql=req.context_sql)
        if not answer:
            raise HTTPException(status_code=502, detail="Empty response from agent.")
        return AskResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to query agent: {e}")
