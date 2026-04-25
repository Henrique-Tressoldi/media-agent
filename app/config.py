"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for the CaseMonks agent."""

    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    google_application_credentials: str = Field(
        ..., alias="GOOGLE_APPLICATION_CREDENTIALS"
    )
    bigquery_project: str = Field(
        default="bigquery-public-data", alias="BIGQUERY_PROJECT"
    )
    bigquery_dataset: str = Field(
        default="thelook_ecommerce", alias="BIGQUERY_DATASET"
    )
    model_name: str = Field(
        default="gemini-2.5-flash", alias="MODEL_NAME"
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
