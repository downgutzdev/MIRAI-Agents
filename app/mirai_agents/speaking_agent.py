import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# carregar .env
load_dotenv(find_dotenv(filename=".env"), override=False)

DEFAULT_SYSTEM = "Você é um assistente amigável, claro e direto. Explique em 2–5 frases quando útil."

def _default_template():
    return PromptTemplate(
        input_variables=["question", "context_sql"],
        template=(
            "Pergunta do usuário:\n{question}\n"
            "{context_sql}\n"
            "Responda de forma cordial e objetiva."
        ),
    )

@dataclass
class FriendlyAgent:
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.4
    system_message: str = DEFAULT_SYSTEM
    template: PromptTemplate = field(default_factory=_default_template)
    transport: str = "rest"
    _llm: Optional[ChatGoogleGenerativeAI] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_GENAI_API_KEY")
        )
        if not api_key:
            raise RuntimeError("Faltando API key. Defina GOOGLE_API_KEY ou GEMINI_API_KEY no .env")

        try:
            self._llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                transport=self.transport,
                api_key=api_key,
            )
        except TypeError:
            self._llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                transport=self.transport,
                google_api_key=api_key,
            )

    def respond(self, question: str, context_sql: Optional[str] = None) -> str:
        if not question or not question.strip():
            return "Me dá um pouco mais de contexto, por favor?"

        ctx = f"\nContexto SQL:\n{context_sql.strip()}" if context_sql else ""
        msg = self.template.format(question=question.strip(), context_sql=ctx)

        resp = self._llm.invoke([
            SystemMessage(content=self.system_message),
            HumanMessage(content=msg)
        ])

        if isinstance(resp, AIMessage):
            return (resp.content or "").strip()
        return (getattr(resp, "content", None) or str(resp)).strip()
