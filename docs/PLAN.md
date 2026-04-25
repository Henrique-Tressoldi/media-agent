# Agente Analista de Mídia Júnior — CaseMonks MVP

**Tipo:** BACKEND (Python + FastAPI + LangGraph + BigQuery)  
**Status:** Em implementação  

## Stack
- Python 3.10+ | FastAPI | LangGraph | Gemini API | BigQuery | Pydantic

## Arquitetura: Tool Calling com LangGraph
- Agente recebe pergunta → LLM decide se precisa de dados → Tool Calling → BigQuery → Insight

## Tools
1. `get_traffic_volume` — Volume de usuários por canal/período
2. `get_channel_performance` — Performance comparativa de canais
3. `get_revenue_by_channel` — Receita detalhada por canal
4. `compare_channels` — Comparação com ROI relativo
