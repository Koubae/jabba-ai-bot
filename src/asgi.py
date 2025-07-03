import logging

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.settings import Settings
from src.core.setup_logger import setup_logger


__all__ = (
    "create_app",
    "setup",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    load_dotenv(find_dotenv())
    settings = setup()
    # logger.info("settings %s", settings)

    # import time
    #
    # emitter_logger = logging.getLogger("emitter")
    # for i in range(10):
    #     emitter_logger.info("info %s", i)
    #     time.sleep(0.8)

    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app_api_cors_allowed_domains,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/index")
    async def read_root():
        return {"Hello": "World"}

    from src.api.infrastructure import router

    app.include_router(router.router, tags=["test"])
    return app


def setup() -> Settings:
    load_dotenv(find_dotenv())

    settings = Settings.get()
    setup_logger(settings)

    logger.info("Application setup completed")
    return settings
