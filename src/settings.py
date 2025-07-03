import os
import sys
import typing as t
from dataclasses import dataclass


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

    # ----------------------------
    #   Redis
    # ----------------------------
    redis_host: str
    redis_port: int
    redis_db: int
    redis_service_prefix: str

    @classmethod
    def get(cls) -> "Settings":
        a = os.getenv("APP_VERSION", "undefined")
        if cls._singleton is None:
            cls._singleton = cls(
                log_level=os.getenv("LOG_LEVEL", "DEBUG"),
                log_format=os.getenv("LOG_FORMAT", "%(asctime)s %(message)s"),
                app_name=os.getenv("APP_NAME", "Jabba AI-Bot"),
                app_version=os.getenv("APP_VERSION", "undefined"),
                app_api_cors_allowed_domains=tuple(
                    os.environ.get("APP_API_CORS_ALLOWED_DOMAINS", "").split(",")
                ),
                redis_host=os.getenv("REDIS_HOST", "localhost"),
                redis_port=int(os.getenv("REDIS_PORT", 6379)),
                redis_db=int(os.getenv("REDIS_DB", 0)),
                redis_service_prefix=os.getenv("REDIS_SERVICE_PREFIX", "ai_bot:"),
            )
        return cls._singleton
