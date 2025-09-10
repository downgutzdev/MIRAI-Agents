from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import os

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Carrega .env
load_dotenv(".env")

# --- SCHEMA padrão ---
DEFAULT_SCHEMA = """
Tabela: alunos
- id (int)
- nome (varchar)
- idade (int)
- curso (varchar)

Tabela: cursos
- id (int)
- nome (varchar)
- duracao_meses (int)

Tabela: professores
- id (int)
- nome (varchar)
- especialidade (varchar)
"""

# --- TEMPLATE do Planner ---
_PLANNER_TEMPLATE = """
## AGENTE PLANNER - ESTRUTURADOR DE PLANOS DE AULA

Você é um agente especializado em planejamento educacional que cria estruturas completas de sessões de estudo, planos de aula detalhados e metodologias de ensino eficazes. Responda sempre de forma objetiva, curta e sem conteúdo desnecessário.

## CONTEXTO EDUCACIONAL:
{context_schema}

## SOLICITAÇÃO DE PLANEJAMENTO:
{question}

## TEMA DA AULA:
{tema}

## OUTPUT ESPERADO:
- Plano de aula estruturado e detalhado
- Cronograma de sessões com tempo definido
- Metodologia clara e objetiva
- Recursos e materiais necessários
- Critérios de avaliação
- Adaptações para diferentes perfis de aluno
"""

def _default_prompt() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["context_schema", "question", "tema"],
        template=_PLANNER_TEMPLATE
    )

@dataclass
class PlannerAgent:
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

        # tenta inicializar de forma resiliente
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
                raise RuntimeError(f"Falha ao inicializar PlannerAgent: {e}")

    def plan(self, question: str, tema: str, context_schema: str | None = None) -> str:
        schema_to_use = context_schema.strip() if context_schema else DEFAULT_SCHEMA
        msg = self.template.format(context_schema=schema_to_use, question=question or "", tema=tema or "")
        resp = self._llm.invoke([HumanMessage(content=msg)])
        if isinstance(resp, AIMessage):
            return (resp.content or "").strip()
        return (getattr(resp, "content", None) or str(resp)).strip()

__all__ = ["PlannerAgent", "DEFAULT_SCHEMA"]
