# app/routers/guardrails_agent.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.mirai_agents.guardrails import analyze_guardrails

router = APIRouter(prefix="/mirai_agents", tags=["mirai_agents"])

# ====== Schemas ======
class GuardrailsRequest(BaseModel):
    question: str = Field(..., min_length=1)
    # campos extras já previstos para futura seleção de modelo/temperatura (opcionais)
    model_name: Optional[str] = Field(default="gemini-1.5-flash")
    temperature: Optional[float] = Field(default=0.1, ge=0.0, le=1.0)

class GuardrailsResponse(BaseModel):
    assessment: Dict[str, Any]

# ====== Routes ======
@router.post("/guardrails/ask", response_model=GuardrailsResponse, status_code=status.HTTP_200_OK)
def ask_guardrails(req: GuardrailsRequest):
    """
    Executa a análise de guardrails e retorna JSON estruturado.
    """
    try:
        # Por enquanto, analyze_guardrails usa o modelo padrão interno (creative_model).
        # Os campos model_name/temperature ficam reservados para evolução.
        out = analyze_guardrails(question=req.question)

        if not out:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Saída vazia do guardrails."
            )

        # Garante dict (se analyze_guardrails retornar string de erro)
        if isinstance(out, str):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Falha no guardrails: {out}"
            )

        return GuardrailsResponse(assessment=out)

    except HTTPException:
        # Relevante para propagar exatamente o status/detalhe já montado
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha no guardrails: {e}"
        )
