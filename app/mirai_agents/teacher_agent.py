from dataclasses import dataclass, field
from typing import Optional
import os

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Carrega .env
load_dotenv(".env")

DEFAULT_PLAN = """
Plano anterior do Planner:
Objetivos: Compreender os fundamentos de Banco de Dados relacionais.
Conteúdo: Modelagem ER, Normalização, SQL básico.
Metodologia: Aula expositiva + exercícios práticos.
Recursos: Slides, banco MySQL, ferramenta BRModelo.
Avaliação: Exercícios práticos e questionário.
Tempo: 2h (1h teoria + 1h prática).
"""

_TEACHER_TEMPLATE = """
## AGENTE PROFESSOR - EDUCADOR DIGITAL RESPONSÁVEL

Você é um agente professor especializado que aplica planos de estudos elaborados pelo planner
e busca conteúdos educacionais confiáveis para proporcionar uma experiência de aprendizagem rica e precisa.

## ASSUNTO ESTUDADO:
{question}

## PLANO DE ESTUDOS A SER APLICADO:
{plan}

## CONTEXTO DA ÚLTIMA SESSÃO (opcional):
{context_schema}

## OUTPUT ESPERADO:
- Aula estruturada conforme o plano do planner
- Conteúdo verificado em múltiplas fontes
- Explicações claras e objetivas
- Exemplos práticos e relevantes
- Verificação de compreensão do aluno
- Próximos passos conforme cronograma
"""

def _default_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["question", "plan", "context_schema"],
        template=_TEACHER_TEMPLATE
    )

@dataclass
class TeacherAgent:
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.4
    template: PromptTemplate = field(default_factory=_default_prompt)
    _llm: Optional[ChatGoogleGenerativeAI] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_GENAI_API_KEY")
        )
        if not api_key:
            raise RuntimeError("API key ausente. Defina GOOGLE_API_KEY ou GEMINI_API_KEY no .env")

        self._llm = None
        try:
            self._llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                transport="rest",
                api_key=api_key,
            )
        except Exception:
            try:
                self._llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    transport="rest",
                    google_api_key=api_key,
                )
            except Exception as e:
                raise RuntimeError(f"Falha ao inicializar TeacherAgent: {e}")

    def teach(self, question: str, plan: str | None = None, context_schema: str | None = None) -> str:
        plan_to_use = plan.strip() if plan and plan.strip() else DEFAULT_PLAN
        msg = self.template.format(
            question=question or "",
            plan=plan_to_use,
            context_schema=context_schema or "Nenhum contexto anterior"
        )
        resp = self._llm.invoke([HumanMessage(content=msg)])
        if isinstance(resp, AIMessage):
            return (resp.content or "").strip()
        return (getattr(resp, "content", None) or str(resp)).strip()

__all__ = ["TeacherAgent", "DEFAULT_PLAN"]
