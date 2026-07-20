from __future__ import annotations

from typing import Any
from functools import lru_cache
from google.oauth2 import service_account
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openrouter import ChatOpenRouter
from langchain_openai import ChatOpenAI

from src.core.settings import settings


class LLMService:
    def __init__(self):
        self.settings = settings

    # ==========================================================================
    # Gemini
    # ==========================================================================
    def _create_gemini(
        self,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> ChatGoogleGenerativeAI:
        credentials = service_account.Credentials.from_service_account_file(
            self.settings.GOOGLE_APPLICATION_CREDENTIALS,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        return ChatGoogleGenerativeAI(
            model=self.settings.GOOGLE_MODEL,
            credentials=credentials,
            project=self.settings.GOOGLE_CLOUD_PROJECT,
            location=self.settings.GOOGLE_CLOUD_LOCATION,
            vertexai=True,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # ==========================================================================
    # Open Router
    # ==========================================================================
    def _create_openrouter(
        self,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> ChatOpenRouter:
        return ChatOpenRouter(
            model=self.settings.OPENROUTER_MODEL,
            api_key=self.settings.OPENROUTER_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # ==========================================================================
    # OpenAI
    # ==========================================================================
    def _create_openai(
        self,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> ChatOpenAI:
        config = self.settings.resolve_openai_config()
        print(f"Model Configuration: \n{config.get("model")}")
        return ChatOpenAI(
            model=config["model"],
            api_key=config["api_key"],
            base_url=config["base_url"],
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # ==========================================================================
    # LLM Factory
    # ==========================================================================
    def create_llm(
        self,
        provider: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> Any:

        provider = (provider or self.settings.LLM_PROVIDER).lower()

        providers = {
            "gemini": self._create_gemini,
            "openrouter": self._create_openrouter,
            "openai": self._create_openai,
        }

        if provider not in providers:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        return providers[provider](
            temperature=temperature,
            max_tokens=max_tokens,
        )


llm = LLMService().create_llm()

# if __name__ == "__main__":
#     res = llm.invoke("Hello")
#     print(res)