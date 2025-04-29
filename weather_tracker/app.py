from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request

from weather_tracker.config import Config
from weather_tracker.ioc import AppProvider
from weather_tracker.logger import setup_package_logger
from weather_tracker.presentation.exception_handlers import register_exception_handlers
from weather_tracker.presentation.handlers import router
from weather_tracker.presentation.middlewares import register_middlewares

config = Config.from_env()


def create_app() -> FastAPI:
    setup_package_logger()
    app = FastAPI()
    app.include_router(router)
    register_exception_handlers(app=app)
    register_middlewares(app=app)
    return app


def create_production_app() -> FastAPI:
    app = create_app()
    container = make_async_container(AppProvider(), context={Config: config})
    setup_dishka(container=container, app=app)
    return app
