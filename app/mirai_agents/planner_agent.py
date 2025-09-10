from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import os

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env
load_dotenv(".env")

# --- Default schema ---
DEFAULT_SCHEMA = """
Table: alunos
- id (int)
- nome (varchar)
- idade (int)
- curso (varchar)

Table: cursos
- id (int)
- nome (varchar)
- duracao_meses (int)

Table: professores
- id (int)
- nome (varchar)
- especialidade (varchar)
"""

# --- Planner Template ---
_PLANNER_TEMPLATE = """
## PLANNER AGENT - LESSON PLAN STRUCTURER

You are an agent specialized in educational planning that creates complete structures for study sessions, detailed lesson plans, and effective teaching methodologies. Always respond in an objective, concise way without unnecessary content.

## EDUCATIONAL CONTEXT:
{context_schema}

## PLANNING REQUEST:
{question}

## LESSON TOPIC:
{tema}

## EXPECTED OUTPUT:
- Structured and detailed lesson plan
- Schedule of sessions with defined time
- Clear and objective methodology
- Required resources and materials
- Evaluation criteria
- Adaptations for different student profiles
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
            raise RuntimeError("Missing API key. Define GOOGLE_API_KEY or GEMINI_API_KEY in .env")

        # Try to initialize resiliently
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
                raise RuntimeError(f"Failed to initialize PlannerAgent: {e}")

    def plan(self, question: str, tema: str, context_schema: str | None = None) -> str:
        schema_to_use = context_schema.strip() if context_schema else DEFAULT_SCHEMA
        msg = self.template.format(context_schema=schema_to_use, question=question or "", tema=tema or "")
        resp = self._llm.invoke([HumanMessage(content=msg)])
        if isinstance(resp, AIMessage):
            return (resp.content or "").strip()
        return (getattr(resp, "content", None) or str(resp)).strip()

__all__ = ["PlannerAgent", "DEFAULT_SCHEMA"]
