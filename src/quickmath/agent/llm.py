"""Build the chat client from environment variables (.env is loaded automatically).

Azure OpenAI is used when AZURE_OPENAI_ENDPOINT is set; otherwise plain OpenAI.
See .env.example for the variables.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI


class ConfigError(RuntimeError):
    pass


def load_client() -> tuple[OpenAI, str]:
    """Return (client, model). For Azure, `model` is the deployment name."""
    load_dotenv()

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if endpoint:
        api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        if not api_key or not deployment:
            raise ConfigError("Azure OpenAI needs AZURE_OPENAI_API_KEY (or OPENAI_API_KEY) and AZURE_OPENAI_DEPLOYMENT.")
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=os.getenv("OPENAI_API_VERSION", "2024-10-21"),
        )
        return client, deployment

    if not os.getenv("OPENAI_API_KEY"):
        raise ConfigError("Set AZURE_OPENAI_ENDPOINT (+ key and deployment) for Azure, or OPENAI_API_KEY for OpenAI.")
    return OpenAI(), os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
