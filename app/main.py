"""FastAPI application — CaseMonks Media Analyst Agent.

Endpoints:
    POST /chat : Send a question to the media analyst agent.
    GET  /health : Health check.
"""

from __future__ import annotations

import logging
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault(
    "GOOGLE_APPLICATION_CREDENTIALS",
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
)

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.graph import build_graph
from app.models.api_models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ToolUsage,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

agent_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: compile the agent graph once."""
    global agent_graph
    logger.info("Compiling agent graph...")
    agent_graph = build_graph()
    logger.info("Agent is ready to receive questions.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="CaseMonks — Agente Analista de Mídia",
    description=(
        "MVP de Agente de IA Autônomo que atua como Analista de Mídia Júnior. "
        "Consulta o dataset thelook_ecommerce no BigQuery e retorna insights "
        "acionáveis para os times de Mídia e Growth."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
async def root():
    """Redireciona para a interface do chat."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health_check() -> HealthResponse:
    """Endpoint de verificação de integridade."""
    return HealthResponse()


@app.post("/chat", response_model=ChatResponse, tags=["Agente"])
async def chat(request: ChatRequest) -> ChatResponse:
    """Enviar uma pergunta ao agente analista de mídia.

    O agente irá:
    1. Analisar a intenção da pergunta.
    2. Decidir qual(is) ferramenta(s) do BigQuery chamar.
    3. Executar consultas SQL parametrizadas.
    4. Retornar um insight acionável — não apenas dados brutos.
    """
    if agent_graph is None:
        raise HTTPException(status_code=503, detail="Agent not initialized.")

    logger.info("Received question: %s", request.question)

    try:
        result = await _invoke_agent(request.question)
        return result
    except RuntimeError as exc:
        logger.error("Agent error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado: {exc}",
        ) from exc


async def _invoke_agent(question: str) -> ChatResponse:
    """Run the LangGraph agent and extract structured response."""
    input_state = {"messages": [HumanMessage(content=question)]}

    final_state = agent_graph.invoke(input_state)

    messages = final_state["messages"]
    tools_used: list[ToolUsage] = []
    raw_data: dict | None = None
    answer = ""

    for msg in messages:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tools_used.append(
                    ToolUsage(
                        tool_name=tc["name"],
                        description=f"Argumentos: {tc.get('args', {})}",
                    )
                )

    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        content = last_message.content
        if isinstance(content, str):
            answer = content or "Não foi possível gerar uma resposta."
        elif isinstance(content, list):
            text_parts = [
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            ]
            answer = "\n".join(text_parts) or "Não foi possível gerar uma resposta."
        else:
            answer = str(content)
    else:
        answer = str(last_message.content)

    return ChatResponse(
        answer=answer,
        tools_used=tools_used,
        data=raw_data,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
