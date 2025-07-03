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

    @classmethod
    def get(cls) -> "Settings":
        if cls._singleton is None:
            cls._singleton = cls(
                log_level=os.getenv("LOG_LEVEL", "DEBUG"),
                log_format=os.getenv("LOG_FORMAT", "%(asctime)s %(message)s"),
            )
        return cls._singleton
