# main.py (na raiz do projeto)

from dotenv import load_dotenv
from pathlib import Path

# Carrega .env cedo (antes de importar a app)
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
    description="API para orquestrar agentes do projeto Mirai"
)

# Configuração de CORS (ajuste allow_origins em produção!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # em produção defina domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos routers
app.include_router(natural_router)
app.include_router(guardrails_router)
app.include_router(planner_router)
app.include_router(professor_router)
app.include_router(schema_agent_router)

# Endpoint de healthcheck
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=9200, reload=True)
