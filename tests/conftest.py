import os
import pytest

# Ensure no real credentials are used during tests
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/dev/null"
os.environ["OPENAI_API_KEY"] = "mock_openai_api_key"
os.environ["GEMINI_API_KEY"] = "mock_gemini_api_key"

@pytest.fixture
def mock_bigquery_client(mocker):
    """Mocks the BigQuery client to avoid real network requests."""
    # Mock google.cloud.bigquery.Client
    mock_client = mocker.patch("app.tools.bigquery_tools._get_client")
    mock_client_instance = mocker.MagicMock()
    mock_client.return_value = mock_client_instance
    return mock_client_instance
