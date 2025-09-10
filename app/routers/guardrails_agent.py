# app/routers/guardrails_agent.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.mirai_agents.guardrails import analyze_guardrails

router = APIRouter(prefix="/mirai_agents", tags=["mirai_agents"])

# ====== Schemas ======
class GuardrailsRequest(BaseModel):
    question: str = Field(..., min_length=1)
    # extra fields already anticipated for future model/temperature selection (optional)
    model_name: Optional[str] = Field(default="gemini-1.5-flash")
    temperature: Optional[float] = Field(default=0.1, ge=0.0, le=1.0)

class GuardrailsResponse(BaseModel):
    assessment: Dict[str, Any]

# ====== Routes ======
@router.post("/guardrails/ask", response_model=GuardrailsResponse, status_code=status.HTTP_200_OK)
def ask_guardrails(req: GuardrailsRequest):
    """
    Executes guardrails analysis and returns structured JSON.
    """
    try:
        # For now, analyze_guardrails uses the default internal model (creative_model).
        # Fields model_name/temperature are reserved for future use.
        out = analyze_guardrails(question=req.question)

        if not out:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Empty output from guardrails."
            )

        # Ensure dict (in case analyze_guardrails returns an error string)
        if isinstance(out, str):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Guardrails failure: {out}"
            )

        return GuardrailsResponse(assessment=out)

    except HTTPException:
        # Important to propagate the exact status/detail already built
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Guardrails failure: {e}"
        )
