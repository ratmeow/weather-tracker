from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from weather_tracker.application.exceptions import (
    LoginRequirementError,
    PasswordRequirementError,
    UserAlreadyExistsError,
    UserLocationError,
    UserNotFoundError,
    WrongPasswordError,
)
from weather_tracker.infrastructure.external_api.exceptions import OpenWeatherClientError
from weather_tracker.infrastructure.httpl_client.exceptions import AsyncClientInternalError
from weather_tracker.infrastructure.session_gateway import RedisInternalError, SessionNotFoundError


class ExceptionResponseFactory:
    def __init__(self, status_code: int):
        self.status_code = status_code

    def __call__(self, request: Request, exception: Exception) -> JSONResponse:
        return JSONResponse(
            content={"message": getattr(exception, "message", str(exception))},
            status_code=self.status_code,
        )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(LoginRequirementError, ExceptionResponseFactory(422))
    app.add_exception_handler(PasswordRequirementError, ExceptionResponseFactory(422))
    app.add_exception_handler(UserAlreadyExistsError, ExceptionResponseFactory(409))
    app.add_exception_handler(UserNotFoundError, ExceptionResponseFactory(404))
    app.add_exception_handler(WrongPasswordError, ExceptionResponseFactory(401))
    app.add_exception_handler(AsyncClientInternalError, ExceptionResponseFactory(500))
    app.add_exception_handler(OpenWeatherClientError, ExceptionResponseFactory(500))
    app.add_exception_handler(UserLocationError, ExceptionResponseFactory(400))
    app.add_exception_handler(RedisInternalError, ExceptionResponseFactory(500))
    app.add_exception_handler(SessionNotFoundError, ExceptionResponseFactory(401))
