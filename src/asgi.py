import logging

from dotenv import find_dotenv, load_dotenv

from src.settings import Settings
from src.core.setup_logger import setup_logger


__all__ = (
    "create_app",
    "setup",
)
logger = logging.getLogger(__name__)


def create_app():
    load_dotenv(find_dotenv())
    settings = setup()
    # logger.info("settings %s", settings)

    # import time
    #
    # emitter_logger = logging.getLogger("emitter")
    # for i in range(10):
    #     emitter_logger.info("info %s", i)
    #     time.sleep(0.8)


def setup() -> Settings:
    load_dotenv(find_dotenv())

    settings = Settings.get()
    setup_logger(settings)

    logger.info("Application setup completed")
    return settings
