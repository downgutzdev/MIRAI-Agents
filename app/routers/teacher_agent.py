from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from app.mirai_agents.teacher_agent import TeacherAgent  # ajuste se o módulo tiver outro nome

router = APIRouter(prefix="/mirai_agents", tags=["mirai_agents"])


class ProfessorRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Pergunta do usuário ou tópico a ser ensinado")
    plan: str = Field(..., min_length=1, description="Plano de estudos a ser aplicado")
    context_schema: Optional[str] = Field(None, description="Contexto da última aula (opcional)")
    model_name: str = Field("gemini-1.5-flash")
    temperature: float = Field(0.4, ge=0.0, le=1.0)


class ProfessorResponse(BaseModel):
    lesson: str


@router.post("/professor/ask", response_model=ProfessorResponse, status_code=status.HTTP_200_OK)
def teach(req: ProfessorRequest):
    try:
        agent = TeacherAgent(model_name=req.model_name, temperature=req.temperature)
        output = agent.teach(
            question=req.question,
            plan=req.plan,
            context_schema=req.context_schema  # ✅ agora vai pro template do Teacher
        )
        if not output:
            raise HTTPException(status_code=502, detail="Saída vazia do professor.")
        return ProfessorResponse(lesson=output)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha no professor: {e}")
