from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from app.mirai_agents.teacher_agent import TeacherAgent  # adjust if the module has another name

router = APIRouter(prefix="/mirai_agents", tags=["mirai_agents"])


class ProfessorRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question or topic to be taught")
    plan: str = Field(..., min_length=1, description="Study plan to be applied")
    context_schema: Optional[str] = Field(None, description="Context of the last class (optional)")
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
            context_schema=req.context_schema  # ✅ now passed to Teacher template
        )
        if not output:
            raise HTTPException(status_code=502, detail="Empty output from teacher.")
        return ProfessorResponse(lesson=output)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Teacher failure: {e}")
