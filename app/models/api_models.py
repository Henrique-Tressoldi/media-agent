"""Pydantic models for API request and response payloads."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Pergunta recebida do usuário."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Pergunta em linguagem natural sobre tráfego, canais ou vendas.",
        examples=[
            "Como foi o volume de usuários vindos de 'Search' no último mês?",
            "Qual dos canais tem a melhor performance? E por que?",
        ],
    )


class ToolUsage(BaseModel):
    """Registro de uma invocação de ferramenta durante o raciocínio do agente."""

    tool_name: str
    description: str


class ChatResponse(BaseModel):
    """Resposta do agente com insight e metadados."""

    answer: str = Field(..., description="Insight acionável gerado pelo agente.")
    tools_used: list[ToolUsage] = Field(
        default_factory=list,
        description="Lista de tools utilizadas durante o raciocínio.",
    )
    data: dict | None = Field(
        default=None,
        description="Dados brutos retornados pelas queries, quando disponíveis.",
    )


class HealthResponse(BaseModel):
    """Resposta da verificação de integridade."""

    status: str = "ok"
    service: str = "casemonks-media-agent"
    version: str = "1.0.0"
