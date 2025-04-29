import logging
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse

from weather_tracker.application.dto import LocationAddInput, LoginUserInput, RegisterUserInput
from weather_tracker.application.use_cases import (
    AddUserLocation,
    GetUserLocations,
    LoginUser,
    LogoutUser,
    RegisterUser,
    RemoveUserLocation,
    SearchLocation,
)
from weather_tracker.domain.value_objects import Coordinates

from .schemas import (
    LocationRequest,
    LocationResponse,
    UserLoginRequest,
    UserRegisterRequest,
    WeatherResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def get_session_id(request: Request) -> str:
    if not request.cookies.get("session_id", False):
        raise HTTPException(status_code=401)
    return request.cookies["session_id"]


@router.post("/register")
@inject
async def register_user(data: UserRegisterRequest, use_case: FromDishka[RegisterUser]):
    await use_case.execute(user_data=RegisterUserInput(login=data.login, password=data.password))
    return Response(status_code=200)


@router.post("/login")
@inject
async def login_user_api(data: UserLoginRequest, use_case: FromDishka[LoginUser]):
    user_session = await use_case.execute(user_data=LoginUserInput(login=data.login, password=data.password))
    response = JSONResponse(content={"username": data.login})
    response.set_cookie(key="session_id", value=str(user_session.session_id), expires=user_session.expired_ts)
    return response


@router.post("/logout")
@inject
async def logout_user_api(user_case: FromDishka[LogoutUser], session_id: str = Depends(get_session_id)):
    await user_case.execute(session_id=session_id)
    response = Response(status_code=200)
    response.delete_cookie(key="session_id")
    return response


@router.get("/locations")
@inject
async def locations_api(
    use_case: FromDishka[GetUserLocations], session_id: str = Depends(get_session_id)
) -> list[WeatherResponse]:
    locations = await use_case.execute(session_id=session_id)
    weather = [WeatherResponse(**loc.to_dict()) for loc in locations]
    return weather


@router.get("/search")
@inject
async def location_search_api(location_name: str, use_case: FromDishka[SearchLocation]) -> list[LocationResponse]:
    locations = await use_case.execute(location_name=location_name)
    response = [LocationResponse(**loc.to_dict()) for loc in locations]
    return response


@router.post("/search")
@inject
async def location_add_api(
    data: LocationRequest, use_case: FromDishka[AddUserLocation], session_id: str = Depends(get_session_id)
):
    await use_case.execute(
        session_id=session_id,
        location_data=LocationAddInput(
            name=data.name, coordinates=Coordinates(latitude=data.latitude, longitude=data.longitude)
        ),
    )
    return Response(status_code=200)


@router.delete("/")
@inject
async def location_delete_api(
    data: Annotated[LocationRequest, Query()],
    use_case: FromDishka[RemoveUserLocation],
    session_id: str = Depends(get_session_id),
):
    await use_case.execute(
        session_id=session_id,
        location_data=LocationAddInput(
            name=data.name, coordinates=Coordinates(latitude=data.latitude, longitude=data.longitude)
        ),
    )
    return Response(status_code=200)
