from dataclasses import dataclass, field
from typing import Optional
import os

from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env
load_dotenv(".env")

DEFAULT_PLAN = """
Previous Planner Plan:
Objectives: Understand the fundamentals of relational databases.
Content: ER modeling, Normalization, basic SQL.
Methodology: Lecture + practical exercises.
Resources: Slides, MySQL database, BRModelo tool.
Assessment: Practical exercises and quiz.
Time: 2h (1h theory + 1h practice).
"""

_TEACHER_TEMPLATE = """
## TEACHER AGENT - RESPONSIBLE DIGITAL EDUCATOR

You are a specialized teacher agent that applies study plans created by the planner
and seeks reliable educational content to provide a rich and accurate learning experience.

## SUBJECT STUDIED:
{question}

## STUDY PLAN TO BE APPLIED:
{plan}

## CONTEXT OF THE LAST SESSION (optional):
{context_schema}

## EXPECTED OUTPUT:
- Lesson structured according to the planner's plan
- Content verified from multiple sources
- Clear and objective explanations
- Practical and relevant examples
- Student comprehension check
- Next steps according to the schedule
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
            raise RuntimeError("Missing API key. Define GOOGLE_API_KEY or GEMINI_API_KEY in .env")

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
                raise RuntimeError(f"Failed to initialize TeacherAgent: {e}")

    def teach(self, question: str, plan: str | None = None, context_schema: str | None = None) -> str:
        plan_to_use = plan.strip() if plan and plan.strip() else DEFAULT_PLAN
        msg = self.template.format(
            question=question or "",
            plan=plan_to_use,
            context_schema=context_schema or "No previous context"
        )
        resp = self._llm.invoke([HumanMessage(content=msg)])
        if isinstance(resp, AIMessage):
            return (resp.content or "").strip()
        return (getattr(resp, "content", None) or str(resp)).strip()

__all__ = ["TeacherAgent", "DEFAULT_PLAN"]
