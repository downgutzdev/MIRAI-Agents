# main.py (at the project root)

from dotenv import load_dotenv
from pathlib import Path

# Load .env early (before importing the app)
load_dotenv(Path(".env"), override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.routers.natural_agent import router as natural_router
from app.routers.guardrails_agent import router as guardrails_router
from app.routers.planner_agent import router as planner_router
from app.routers.teacher_agent import router as professor_router
from app.routers.schema_agent import router as schema_agent_router

app = FastAPI(
    title="Mirai Agents API",
    version="1.0.0",
    description="API to orchestrate Mirai project agents"
)

# CORS configuration (adjust allow_origins in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # in production define specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(natural_router)
app.include_router(guardrails_router)
app.include_router(planner_router)
app.include_router(professor_router)
app.include_router(schema_agent_router)

# Healthcheck endpoint
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=9200, reload=True)
