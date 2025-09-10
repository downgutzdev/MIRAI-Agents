import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise RuntimeError("API KEY not found")

creative_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=gemini_api_key,
    temperature=0.7,
)

logical_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=gemini_api_key,
    temperature=0.1,
)
