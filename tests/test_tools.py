import json
from app.tools.bigquery_tools import (
    get_traffic_volume,
    get_channel_performance,
    get_revenue_by_channel,
    compare_channels,
)

def test_get_traffic_volume(mocker):
    # Mock _run_query instead of the client
    mock_run_query = mocker.patch("app.tools.bigquery_tools._run_query")
    mock_run_query.return_value = [{"canal": "Search", "total_usuarios": 100}]

    result = get_traffic_volume.invoke({
        "traffic_source": "Search",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    })

    assert isinstance(result, str)
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["total_usuarios"] == 100
    mock_run_query.assert_called_once()


def test_get_channel_performance(mocker):
    mock_run_query = mocker.patch("app.tools.bigquery_tools._run_query")
    mock_run_query.return_value = [{"canal": "Search", "receita_total": 500.50}]

    result = get_channel_performance.invoke({
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    })

    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["receita_total"] == 500.50


def test_get_revenue_by_channel(mocker):
    mock_run_query = mocker.patch("app.tools.bigquery_tools._run_query")
    mock_run_query.return_value = [{"canal": "Organic", "receita": 1200.0}]

    result = get_revenue_by_channel.invoke({
        "traffic_source": "Organic",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    })

    data = json.loads(result)
    assert data[0]["receita"] == 1200.0


def test_compare_channels(mocker):
    mock_run_query = mocker.patch("app.tools.bigquery_tools._run_query")
    mock_run_query.return_value = [
        {"canal": "Search", "receita": 500.0},
        {"canal": "Organic", "receita": 300.0}
    ]

    result = compare_channels.invoke({
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    })

    data = json.loads(result)
    assert len(data) == 2
    assert data[0]["canal"] == "Search"
