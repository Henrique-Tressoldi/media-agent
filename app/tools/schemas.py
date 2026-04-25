"""Pydantic schemas for BigQuery tool inputs and outputs."""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Dataset schema documentation (used in prompts to prevent SQL hallucination)
# ---------------------------------------------------------------------------
THELOOK_SCHEMA = """
Dataset: bigquery-public-data.thelook_ecommerce

### Tabela: users
| Coluna          | Tipo      | Descrição                              |
|-----------------|-----------|----------------------------------------|
| id              | INTEGER   | ID único do usuário                    |
| traffic_source  | STRING    | Origem do tráfego (Search, Organic, Facebook, Display Ads, Email, YouTube) |
| created_at      | TIMESTAMP | Data de criação do usuário             |
| first_name      | STRING    | Nome                                   |
| last_name       | STRING    | Sobrenome                              |
| email           | STRING    | E-mail                                 |
| age             | INTEGER   | Idade                                  |
| gender          | STRING    | Gênero                                 |
| country         | STRING    | País                                   |
| city            | STRING    | Cidade                                 |

### Tabela: orders
| Coluna          | Tipo      | Descrição                              |
|-----------------|-----------|----------------------------------------|
| order_id        | INTEGER   | ID único do pedido                     |
| user_id         | INTEGER   | FK → users.id                          |
| status          | STRING    | Status (Complete, Cancelled, etc)      |
| created_at      | TIMESTAMP | Data do pedido                         |
| num_of_item     | INTEGER   | Quantidade de itens no pedido          |

### Tabela: order_items
| Coluna          | Tipo      | Descrição                              |
|-----------------|-----------|----------------------------------------|
| id              | INTEGER   | ID do item                             |
| order_id        | INTEGER   | FK → orders.order_id                   |
| product_id      | INTEGER   | ID do produto                          |
| sale_price      | FLOAT     | Preço de venda do item                 |
| status          | STRING    | Status do item                         |

### Canais de tráfego válidos (traffic_source):
- Search
- Organic
- Facebook
- Display Ads
- Email
- YouTube
"""


# ---------------------------------------------------------------------------
# Tool input schemas
# ---------------------------------------------------------------------------
class TrafficVolumeInput(BaseModel):
    """Input for querying user traffic volume by channel."""

    traffic_source: str | None = Field(
        default=None,
        description=(
            "Canal de tráfego a filtrar. Valores válidos: "
            "Search, Organic, Facebook, Display Ads, Email, YouTube. "
            "Se None, retorna todos os canais."
        ),
    )
    start_date: str = Field(
        ...,
        description="Data início no formato YYYY-MM-DD.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        ...,
        description="Data final no formato YYYY-MM-DD.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class ChannelPerformanceInput(BaseModel):
    """Input for querying channel performance comparison."""

    start_date: str = Field(
        ...,
        description="Data início no formato YYYY-MM-DD.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        ...,
        description="Data final no formato YYYY-MM-DD.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class RevenueByChannelInput(BaseModel):
    """Input for querying revenue details by channel."""

    traffic_source: str | None = Field(
        default=None,
        description=(
            "Canal de tráfego a filtrar. Se None, retorna todos."
        ),
    )
    start_date: str = Field(
        ...,
        description="Data início no formato YYYY-MM-DD.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        ...,
        description="Data final no formato YYYY-MM-DD.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class CompareChannelsInput(BaseModel):
    """Input for comparing all channels side by side."""

    start_date: str = Field(
        ...,
        description="Data início no formato YYYY-MM-DD.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        ...,
        description="Data final no formato YYYY-MM-DD.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
