# backend/src/core/settings.py

import json
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]
# print(BASE_DIR)

class Settings(BaseSettings):
    """Application Settings."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # ignore unknown env vars
    )

    # ==========================================================================
    # Application
    # ==========================================================================
    APP_NAME: str = "Blog Writing Agent"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    RELOAD: bool = False
    LOG_LEVEL: str = "DEBUG" # "INFO" | "DEBUG"
    LLM_PROVIDER: str = "openai" # "gemini" | "openai" | "openrouter"
    CUSTOM_PROVIDER: str | None = None  # "opencode" | "groq" | "nvidia" | None - To use custom llm, set LLM_PROVIDER=openai

    # ==========================================================================
    # Tavily
    # ==========================================================================
    TAVILY_API_KEY: str | None = None

    # ==========================================================================
    # Gemini
    # ==========================================================================
    GOOGLE_MODEL: str = "gemini-2.5-flash"
    GOOGLE_API_KEY: str | None = None
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "global"
    GOOGLE_APPLICATION_CREDENTIALS: str

    # ==========================================================================
    # OPENAI
    # ==========================================================================
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None

    # ==========================================================================
    # OpenRouter
    # ==========================================================================
    OPENROUTER_MODEL: str = "google/gemma-4-26b-a4b-it:free"
    OPENROUTER_API_KEY: str
    
    # ==========================================================================
    # OpenCode
    # ==========================================================================
    OPENCODE_MODEL: str = "deepseek-v4-flash-free"
    OPENCODE_API_KEY: str | None = None
    OPENCODE_BASE_URL: str | None = None

    # ==========================================================================
    # Groq
    # ==========================================================================
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    GROQ_API_KEY: str | None = None
    GROQ_BASE_URL: str | None = None

    # ==========================================================================
    # Nvidia
    # ==========================================================================
    NVIDIA_MODEL: str | None = None
    NVIDIA_API_KEY: str | None = None
    NVIDIA_BASE_URL: str | None = None

    # ==========================================================================
    # Paths
    # ==========================================================================
    PROJECT_ROOT: Path = BASE_DIR
    PROMPTS_DIR: Path = BASE_DIR / "backend" / "src" / "prompts"
    MODEL_CONFIG_PATH: Path = BASE_DIR / "backend" / "src" / "config" / "model_config_map.json"
    LOGS_DIR: Path = BASE_DIR / "LOGS"
    OUTPUT_DIR: Path = BASE_DIR / "output"

    # ==========================================================================
    # Directory Management
    # ==========================================================================
    def create_directories(self) -> None:
        """
        Create all required application directories.
        """
        directories = [
            self.LOGS_DIR,
            self.OUTPUT_DIR
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    # ==========================================================================
    # OpenAI-slot resolution
    # ==========================================================================
    def resolve_openai_config(self) -> dict[str, str | None]:
        """
        Resolves the effective (model, api_key, base_url) to use for the
        "openai" provider slot.

        - If CUSTOM_PROVIDER is unset, returns the standard OPENAI_* values.
        - If CUSTOM_PROVIDER is set (e.g. "opencode"), looks up the
          field-name mapping in model_configuration.json and pulls the
          corresponding values off this Settings instance.
        """
        if not self.CUSTOM_PROVIDER or self.CUSTOM_PROVIDER == "None":
            print("=== USING OPENAI STANDARD MODEL CONFIG ===")
            return {
                "model": self.OPENAI_MODEL,
                "api_key": self.OPENAI_API_KEY,
                "base_url": self.OPENAI_BASE_URL,
            }

        if not self.MODEL_CONFIG_PATH.exists():
            raise FileNotFoundError(
                f"Model configuration file not found: {self.MODEL_CONFIG_PATH}"
            )

        print("=== USING CUSTOM MODEL CONFIG ===")

        mapping: dict[str, dict[str, str]] = json.loads(
            self.MODEL_CONFIG_PATH.read_text()
        )

        provider_key = self.CUSTOM_PROVIDER.lower()
        if provider_key not in mapping:
            raise ValueError(
                f"Unknown CUSTOM_PROVIDER '{self.CUSTOM_PROVIDER}'. "
                f"Available: {list(mapping.keys())}"
            )

        field_map = mapping[provider_key]  # {"OPENAI_MODEL": "OPENCODE_MODEL", ...}

        return {
            "model": getattr(self, field_map["OPENAI_MODEL"]),
            "api_key": getattr(self, field_map["OPENAI_API_KEY"]),
            "base_url": getattr(self, field_map["OPENAI_BASE_URL"]),
        }

@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    settings = Settings()
    settings.create_directories()
    return settings


settings = get_settings()