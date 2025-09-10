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

# Load .env (idempotent)
load_dotenv(find_dotenv(filename=".env"), override=False)

# --- TEMPLATE (uses {{ }} in the example to avoid breaking .format) ---
_SCHEMA_TEMPLATE = """
You are a pedagogical agent. Your ONLY task is to assess a student's strengths, weaknesses,
and general observations from the provided input.

MANDATORY RULES:
- Be concise without losing essential information.
- Return ONLY the defined JSON, no extra text, no ```json fences.
- Do not invent additional fields.
- The JSON MUST have exactly the keys: strong_points, weak_points, general_comments.

Example input:
"I'm not very good at algebra, but I know how to apply formulas. And I hate copying notes."

Example output:
{{
  "strong_points": "Knows how to apply formulas",
  "weak_points": "Not very good at algebra",
  "general_comments": "Doesn't like copying notes"
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
            raise RuntimeError("Missing API key. Define GOOGLE_API_KEY or GEMINI_API_KEY in .env")

        # Resilient initialization for different langchain_google_genai versions
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
        """Convert None / non-string to a safe string (avoid None in response_model)."""
        if v is None:
            return ""
        s = str(v).strip()
        return s

    def evaluate(self, question: str) -> dict:
        """
        ALWAYS returns:
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
                "general_comments": "Empty input"
            }
            print("\n[DEBUG] NORMALIZED RESULT (empty input):\n", json.dumps(result, ensure_ascii=False, indent=2))
            return result

        msg = self.template.format(question=question.strip())
        print("\n[DEBUG] PROMPT SENT TO MODEL:\n", msg)

        # --- Model call ---
        resp = self._llm.invoke([HumanMessage(content=msg)])
        if isinstance(resp, AIMessage):
            raw_text = (resp.content or "").strip()
        else:
            raw_text = (getattr(resp, "content", None) or str(resp)).strip()

        # 🔥 Always log raw
        print("\n================ MODEL RAW =================\n")
        print(raw_text)
        print("\n===========================================\n")

        # --- Clean possible markdown fences ```
        raw_text = re.sub(r"```(?:json)?", "", raw_text, flags=re.IGNORECASE).replace("```", "")

        # --- Try to extract the first JSON block
        match = re.search(r"\{.*?\}", raw_text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in the response (see RAW above).")

        bloco = match.group(0).strip()
        print("\n[DEBUG] EXTRACTED BLOCK FOR PARSE:\n", bloco, "\n")

        # --- Safe parse
        parsed = json.loads(bloco)

        # 🔒 Normalize to strings (never None)
        result = {
            "strong_points": self._norm(parsed.get("strong_points")),
            "weak_points": self._norm(parsed.get("weak_points")),
            "general_comments": self._norm(parsed.get("general_comments")),
        }

        print("\n[DEBUG] NORMALIZED RESULT (no None):\n", json.dumps(result, ensure_ascii=False, indent=2))
        return result


if __name__ == "__main__":
    # Quick local debug
    agent = SchemaAgent()
    question = "I'm terrible at math, good at philosophy, and I hate copying notes."
    print(f"\n[DEBUG] AUTOMAIN TEST - fixed question:\n{question}\n")

    try:
        result = agent.evaluate(question)
        print("\n[DEBUG] FINAL PARSED RESULT:\n", json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        import traceback
        print(f"[ERROR] Failed to evaluate: {e}")
        traceback.print_exc()
