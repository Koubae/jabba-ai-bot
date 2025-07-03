import os
import sys
import typing as t
from dataclasses import dataclass


SUPPORTED_ML_MODELS: t.Final[tuple[str, ...]] = (
    "testings-mock",
    "openchat",
    "neural-chat",
)


@dataclass(frozen=True)
class Settings:
    """Singleton Instance for Application settings"""

    _singleton: t.ClassVar[t.Optional["Settings"]] = None

    ROOT_PATH: t.ClassVar[str] = os.path.dirname(os.path.abspath(sys.argv[0]))
    CONF_PATH: t.ClassVar[str] = os.path.join(ROOT_PATH, "conf")
    TESTS_PATH: t.ClassVar[str] = os.path.join(ROOT_PATH, "tests")

    # ----------------------------
    #   App
    # ----------------------------
    log_level: str
    log_format: str
    app_name: str
    app_version: str
    app_api_cors_allowed_domains: tuple[str, ...]
    app_max_thread_pool_workers: int

    # ----------------------------
    #   Bot
    # ----------------------------
    bot_ml_model: t.Literal["testings-mock", "openchat", "neural-chat"]

    # ----------------------------
    #   Redis
    # ----------------------------
    cache_backend: str
    cache_service_prefix: str

    redis_host: str
    redis_port: int
    redis_db: int
    redis_max_connections: int

    @classmethod
    def get(cls) -> "Settings":
        bot_ml_model: t.Literal["testings-mock", "openchat", "neural-chat"] = (  # noqa
            os.getenv("BOT_ML_MODEL", "testings-mock")
        )
        if bot_ml_model not in SUPPORTED_ML_MODELS:
            raise ValueError(
                f"Unsupported ML model {bot_ml_model}. Supported models are {SUPPORTED_ML_MODELS}"
            )

        if cls._singleton is None:
            cls._singleton = cls(
                log_level=os.getenv("LOG_LEVEL", "DEBUG"),
                log_format=os.getenv("LOG_FORMAT", "%(asctime)s %(message)s"),
                app_name=os.getenv("APP_NAME", "Jabba AI-Bot"),
                app_version=os.getenv("APP_VERSION", "undefined"),
                app_api_cors_allowed_domains=tuple(
                    os.environ.get("APP_API_CORS_ALLOWED_DOMAINS", "").split(",")
                ),
                app_max_thread_pool_workers=int(
                    os.getenv("APP_MAX_THREAD_POOL_WORKERS", 20)
                ),
                bot_ml_model=bot_ml_model,
                cache_backend=os.getenv("CACHE_BACKEND", "redis"),
                cache_service_prefix=os.getenv("CACHE_SERVICE_PREFIX", "ai_bot:"),
                redis_host=os.getenv("REDIS_HOST", "localhost"),
                redis_port=int(os.getenv("REDIS_PORT", 6379)),
                redis_db=int(os.getenv("REDIS_DB", 0)),
                redis_max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", 10)),
            )
        return cls._singleton
