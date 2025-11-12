"""
Configuration settings for the Azure Functions app.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.
    """

    azure_client_id: str
    azure_tenant_id: str
    azure_client_secret: str
    graph_api_scope: str
    graph_api_url: str

    class Config:
        """Pydantic configuration for loading from .env file."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # ignores extra Azure Functions env variables


settings = Settings()
