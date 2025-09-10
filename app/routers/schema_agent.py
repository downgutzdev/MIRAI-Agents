# app/routers/schema_creator_router.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.mirai_agents.schema_agent import SchemaAgent

router = APIRouter(prefix="/mirai_agents", tags=["mirai_agents"])

class EvaluationRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Input with the student's speech or context")
    model_name: str = Field("gemini-1.5-flash")
    temperature: float = Field(0.2, ge=0.0, le=1.0)

class EvaluationResponse(BaseModel):
    strong_points: str
    weak_points: str
    general_comments: str

def _as_str(v: object) -> str:
    if v is None:
        return ""
    return str(v).strip()

@router.post("/schema_creator/ask", response_model=EvaluationResponse, status_code=status.HTTP_200_OK)
def evaluate_student(req: EvaluationRequest):
    try:
        agent = SchemaAgent(model_name=req.model_name, temperature=req.temperature)
        raw = agent.evaluate(req.question)

        # final safeguard so Pydantic doesn't fail on None values
        answer = {
            "strong_points": _as_str(raw.get("strong_points")),
            "weak_points": _as_str(raw.get("weak_points")),
            "general_comments": _as_str(raw.get("general_comments")),
        }

        return EvaluationResponse(**answer)

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to query agent: {e}")
