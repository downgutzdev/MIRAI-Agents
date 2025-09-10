# app/mirai_agents/schema_agent.py
import os
import re
import json
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Carrega .env (idempotente)
load_dotenv(find_dotenv(filename=".env"), override=False)

# --- TEMPLATE (usa {{ }} no exemplo para não quebrar .format) ---
_SCHEMA_TEMPLATE = """
Você é um agente pedagógico. Sua tarefa ÚNICA é avaliar os pontos fortes, fracos
e observações gerais de um estudante a partir da entrada fornecida.

REGRAS (obrigatórias):
- Seja conciso, sem perder informações essenciais.
- Retorne APENAS o JSON definido, sem texto extra, sem ```json.
- Não invente campos adicionais.
- O JSON DEVE ter exatamente as chaves: strong_points, weak_points, general_comments.

Exemplo de input:
"Não sou muito bom em álgebra, mas sei aplicar fórmulas. E odeio copiar matéria."

Exemplo de output:
{{
  "strong_points": "Sabe aplicar fórmulas",
  "weak_points": "Não é muito bom em álgebra",
  "general_comments": "Não gosta de copiar matéria"
}}

INPUT:
{question}
"""

def _default_template() -> PromptTemplate:
    return PromptTemplate(
        input_variables=["question"],
        template=_SCHEMA_TEMPLATE
    )

@dataclass
class SchemaAgent:
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.2
    template: PromptTemplate = field(default_factory=_default_template)
    _llm: Optional[ChatGoogleGenerativeAI] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_GENAI_API_KEY")
        )
        if not api_key:
            raise RuntimeError("Faltando API key. Defina GOOGLE_API_KEY ou GEMINI_API_KEY no .env")

        # inicialização resiliente para diferentes versões do langchain_google_genai
        try:
            self._llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                transport="rest",
                api_key=api_key,
            )
        except TypeError:
            self._llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                transport="rest",
                google_api_key=api_key,
            )

    @staticmethod
    def _norm(v) -> str:
        """Converte None / não-string em string segura (sem None no response_model)."""
        if v is None:
            return ""
        s = str(v).strip()
        return s

    def evaluate(self, question: str) -> dict:
        """
        Retorna SEMPRE:
        {
          "strong_points": str,
          "weak_points": str,
          "general_comments": str
        }
        """
        if not question or not question.strip():
            result = {
                "strong_points": "",
                "weak_points": "",
                "general_comments": "Entrada vazia"
            }
            print("\n[DEBUG] RESULT NORMALIZADO (entrada vazia):\n", json.dumps(result, ensure_ascii=False, indent=2))
            return result

        msg = self.template.format(question=question.strip())
        print("\n[DEBUG] PROMPT ENVIADO AO MODELO:\n", msg)

        # --- Chamada ao modelo ---
        resp = self._llm.invoke([HumanMessage(content=msg)])
        if isinstance(resp, AIMessage):
            raw_text = (resp.content or "").strip()
        else:
            raw_text = (getattr(resp, "content", None) or str(resp)).strip()

        # 🔥 Loga o raw SEMPRE
        print("\n================ RAW DO MODELO ================\n")
        print(raw_text)
        print("\n===============================================\n")

        # --- Limpa possíveis blocos markdown ```
        raw_text = re.sub(r"```(?:json)?", "", raw_text, flags=re.IGNORECASE).replace("```", "")

        # --- Tenta extrair o primeiro bloco JSON
        match = re.search(r"\{.*?\}", raw_text, re.DOTALL)
        if not match:
            raise ValueError("Nenhum JSON encontrado na resposta (veja RAW acima).")

        bloco = match.group(0).strip()
        print("\n[DEBUG] BLOCO EXTRAÍDO PARA PARSE:\n", bloco, "\n")

        # --- Parse seguro
        parsed = json.loads(bloco)

        # 🔒 Normaliza para strings (nunca None)
        result = {
            "strong_points": self._norm(parsed.get("strong_points")),
            "weak_points": self._norm(parsed.get("weak_points")),
            "general_comments": self._norm(parsed.get("general_comments")),
        }

        print("\n[DEBUG] RESULT NORMALIZADO (sem None):\n", json.dumps(result, ensure_ascii=False, indent=2))
        return result


if __name__ == "__main__":
    # Debug local rápido
    agent = SchemaAgent()
    question = "sou pessimo em matematica bom em filosofia e odeio copiar materia"
    print(f"\n[DEBUG] TESTE AUTOMAIN - pergunta fixa:\n{question}\n")

    try:
        result = agent.evaluate(question)
        print("\n[DEBUG] RESULTADO FINAL PARSEADO:\n", json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        import traceback
        print(f"[ERRO] Falha ao avaliar: {e}")
        traceback.print_exc()
