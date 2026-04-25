"""BigQuery tools for the media analyst agent.

Each function is a LangChain-compatible tool that executes parameterized
SQL queries against the thelook_ecommerce dataset. All queries use BigQuery
query parameters to prevent SQL injection.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from google.cloud import bigquery
from langchain_core.tools import tool

from app.tools.schemas import (
    TrafficVolumeInput,
    ChannelPerformanceInput,
    RevenueByChannelInput,
    CompareChannelsInput,
)

logger = logging.getLogger(__name__)

DATASET = "bigquery-public-data.thelook_ecommerce"


def _get_client() -> bigquery.Client:
    """Create an authenticated BigQuery client."""
    return bigquery.Client()


def _run_query(query: str, params: list[bigquery.ScalarQueryParameter]) -> list[dict[str, Any]]:
    """Execute a parameterized BigQuery query and return rows as dicts."""
    client = _get_client()
    job_config = bigquery.QueryJobConfig(query_parameters=params)

    try:
        result = client.query(query, job_config=job_config).result()
        rows = [dict(row) for row in result]
        logger.info("Query executed successfully. Rows returned: %d", len(rows))
        return rows
    except Exception as exc:
        logger.error("BigQuery query failed: %s", exc)
        raise RuntimeError(f"Falha ao consultar BigQuery: {exc}") from exc


# ---------------------------------------------------------------------------
# Tool 1: Traffic Volume
# ---------------------------------------------------------------------------
@tool(args_schema=TrafficVolumeInput)
def get_traffic_volume(
    traffic_source: str | None = None,
    start_date: str = "",
    end_date: str = "",
) -> str:
    """Consulta o volume de usuários (tráfego) agrupado por canal em um período.

    Use esta ferramenta quando o usuário perguntar sobre volume de tráfego,
    quantidade de usuários, ou crescimento de um canal específico.
    """
    source_filter = ""
    params = [
        bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
        bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
    ]

    if traffic_source:
        source_filter = "AND u.traffic_source = @traffic_source"
        params.append(
            bigquery.ScalarQueryParameter("traffic_source", "STRING", traffic_source)
        )

    query = f"""
        SELECT
            u.traffic_source AS canal,
            COUNT(DISTINCT u.id) AS total_usuarios,
            MIN(u.created_at) AS primeiro_registro,
            MAX(u.created_at) AS ultimo_registro
        FROM `{DATASET}.users` u
        WHERE DATE(u.created_at) BETWEEN @start_date AND @end_date
        {source_filter}
        GROUP BY u.traffic_source
        ORDER BY total_usuarios DESC
    """

    rows = _run_query(query, params)
    return json.dumps(rows, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 2: Channel Performance
# ---------------------------------------------------------------------------
@tool(args_schema=ChannelPerformanceInput)
def get_channel_performance(start_date: str, end_date: str) -> str:
    """Compara a performance de todos os canais de tráfego — incluindo
    total de usuários, pedidos completados, receita total e receita média por pedido.

    Use esta ferramenta quando o usuário perguntar qual canal performa melhor,
    pior, ou pedir uma comparação geral de canais.
    """
    params = [
        bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
        bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
    ]

    query = f"""
        SELECT
            u.traffic_source AS canal,
            COUNT(DISTINCT u.id) AS total_usuarios,
            COUNT(DISTINCT o.order_id) AS total_pedidos,
            ROUND(SUM(oi.sale_price), 2) AS receita_total,
            ROUND(AVG(oi.sale_price), 2) AS ticket_medio_item,
            ROUND(
                SAFE_DIVIDE(
                    COUNT(DISTINCT o.order_id),
                    COUNT(DISTINCT u.id)
                ) * 100, 2
            ) AS taxa_conversao_pct
        FROM `{DATASET}.users` u
        LEFT JOIN `{DATASET}.orders` o
            ON u.id = o.user_id
            AND o.status = 'Complete'
            AND DATE(o.created_at) BETWEEN @start_date AND @end_date
        LEFT JOIN `{DATASET}.order_items` oi
            ON o.order_id = oi.order_id
        WHERE DATE(u.created_at) BETWEEN @start_date AND @end_date
        GROUP BY u.traffic_source
        ORDER BY receita_total DESC
    """

    rows = _run_query(query, params)
    return json.dumps(rows, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 3: Revenue by Channel
# ---------------------------------------------------------------------------
@tool(args_schema=RevenueByChannelInput)
def get_revenue_by_channel(
    traffic_source: str | None = None,
    start_date: str = "",
    end_date: str = "",
) -> str:
    """Retorna a receita detalhada por canal, incluindo breakdown mensal.

    Use esta ferramenta quando o usuário perguntar sobre receita, faturamento,
    ou tendência de vendas de um canal ao longo do tempo.
    """
    source_filter = ""
    params = [
        bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
        bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
    ]

    if traffic_source:
        source_filter = "AND u.traffic_source = @traffic_source"
        params.append(
            bigquery.ScalarQueryParameter("traffic_source", "STRING", traffic_source)
        )

    query = f"""
        SELECT
            u.traffic_source AS canal,
            FORMAT_TIMESTAMP('%%Y-%%m', o.created_at) AS mes,
            COUNT(DISTINCT o.order_id) AS pedidos,
            ROUND(SUM(oi.sale_price), 2) AS receita,
            COUNT(DISTINCT u.id) AS usuarios_unicos
        FROM `{DATASET}.users` u
        JOIN `{DATASET}.orders` o ON u.id = o.user_id
        JOIN `{DATASET}.order_items` oi ON o.order_id = oi.order_id
        WHERE o.status = 'Complete'
            AND DATE(o.created_at) BETWEEN @start_date AND @end_date
            {source_filter}
        GROUP BY canal, mes
        ORDER BY canal, mes
    """

    rows = _run_query(query, params)
    return json.dumps(rows, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 4: Compare Channels
# ---------------------------------------------------------------------------
@tool(args_schema=CompareChannelsInput)
def compare_channels(start_date: str, end_date: str) -> str:
    """Gera um resumo comparativo completo de todos os canais, incluindo
    volume, receita, taxa de conversão e ROI relativo entre canais.

    Use esta ferramenta quando o usuário quiser entender qual canal tem
    melhor ROI, ou pedir "todos os dados" de uma vez.
    """
    params = [
        bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
        bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
    ]

    query = f"""
        WITH channel_metrics AS (
            SELECT
                u.traffic_source AS canal,
                COUNT(DISTINCT u.id) AS usuarios,
                COUNT(DISTINCT CASE WHEN o.status = 'Complete' THEN o.order_id END) AS pedidos_completos,
                COUNT(DISTINCT o.order_id) AS pedidos_totais,
                ROUND(SUM(CASE WHEN o.status = 'Complete' THEN oi.sale_price ELSE 0 END), 2) AS receita,
                ROUND(AVG(CASE WHEN o.status = 'Complete' THEN oi.sale_price END), 2) AS ticket_medio
            FROM `{DATASET}.users` u
            LEFT JOIN `{DATASET}.orders` o
                ON u.id = o.user_id
                AND DATE(o.created_at) BETWEEN @start_date AND @end_date
            LEFT JOIN `{DATASET}.order_items` oi
                ON o.order_id = oi.order_id
            WHERE DATE(u.created_at) BETWEEN @start_date AND @end_date
            GROUP BY u.traffic_source
        )
        SELECT
            canal,
            usuarios,
            pedidos_completos,
            receita,
            ticket_medio,
            ROUND(SAFE_DIVIDE(pedidos_completos, usuarios) * 100, 2) AS taxa_conversao_pct,
            ROUND(SAFE_DIVIDE(receita, usuarios), 2) AS receita_por_usuario,
            ROUND(
                SAFE_DIVIDE(receita, SUM(receita) OVER()) * 100, 2
            ) AS share_receita_pct
        FROM channel_metrics
        ORDER BY receita DESC
    """

    rows = _run_query(query, params)
    return json.dumps(rows, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Export all tools
# ---------------------------------------------------------------------------
ALL_TOOLS = [
    get_traffic_volume,
    get_channel_performance,
    get_revenue_by_channel,
    compare_channels,
]
