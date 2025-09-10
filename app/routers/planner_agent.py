from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from app.mirai_agents.planner_agent import PlannerAgent

router = APIRouter(prefix="/mirai_agents", tags=["mirai_agents"])


class PlannerRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Solicitação de planejamento")
    tema: str = Field(..., min_length=1, description="Tema da aula")
    context_schema: Optional[str] = Field(None, description="Contexto opcional da última sessão")
    model_name: str = Field("gemini-1.5-flash")
    temperature: float = Field(0.4, ge=0.0, le=1.0)


class PlannerResponse(BaseModel):
    plan: str


@router.post("/planner/ask", response_model=PlannerResponse, status_code=status.HTTP_200_OK)
def plan(req: PlannerRequest):
    try:
        agent = PlannerAgent(model_name=req.model_name, temperature=req.temperature)
        out = agent.plan(
            question=req.question,
            tema=req.tema,
            context_schema=req.context_schema  # ✅ consistente
        )
        if not out:
            raise HTTPException(status_code=502, detail="Saída vazia do planner.")
        return PlannerResponse(plan=out)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha no planner: {e}")
