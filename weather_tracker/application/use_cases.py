import re
from uuid import UUID

from weather_tracker.domain.entities import Location, User
from weather_tracker.domain.exceptions import DomainError

from .dto import (
    LocationAddInput,
    LocationDTO,
    LocationWeatherDTO,
    LoginUserInput,
    RegisterUserInput,
    RegisterUserOutput,
    UserSessionDTO,
)
from .exceptions import (
    LocationNotFoundError,
    LoginRequirementError,
    PasswordRequirementError,
    UserAlreadyExistsError,
    UserLocationError,
    UserNotFoundError,
    WrongPasswordError,
)
from .interfaces import (
    DBSession,
    Hasher,
    LocationGateway,
    UserGateway,
    UserSessionGateway,
    WeatherClient,
)


class RegisterUser:
    def __init__(self, user_gateway: UserGateway, hasher: Hasher, db_session: DBSession):
        self.user_gateway = user_gateway
        self.hasher = hasher
        self.db_session = db_session

    async def execute(self, user_data: RegisterUserInput) -> RegisterUserOutput:
        if not self._is_valid_login(login=user_data.login):
            raise LoginRequirementError()

        if not self._is_strong_password(password=user_data.password):
            raise PasswordRequirementError()

        if await self.user_gateway.find_by_login(login=user_data.login) is not None:
            raise UserAlreadyExistsError()

        user = User.create(login=user_data.login, hashed_password=self.hasher.hash(text=user_data.password))

        await self.user_gateway.save(user=user)
        await self.db_session.commit()
        return RegisterUserOutput(login=user.login, hashed_password=user.hashed_password)

    @staticmethod
    def _is_valid_login(login: str) -> bool:
        pattern = r"^[A-Za-z\d!@#$%^&*]{3,}$"
        return bool(re.fullmatch(pattern, login))

    @staticmethod
    def _is_strong_password(password: str) -> bool:
        pattern = r"^[A-Za-z\d!@#$%^&*_]{8,}$"
        has_required_char = bool(re.search(r"[\d!@#$%^&*_]", password))
        return bool(re.fullmatch(pattern, password)) and has_required_char


class LoginUser:
    def __init__(self, user_gateway: UserGateway, hasher: Hasher, user_session_gateway: UserSessionGateway):
        self.user_gateway = user_gateway
        self.hasher = hasher
        self.user_session_gateway = user_session_gateway

    async def execute(self, user_data: LoginUserInput) -> UserSessionDTO:
        user = await self.user_gateway.find_by_login(login=user_data.login)
        if user is None:
            raise UserNotFoundError(login=user_data.login)

        if not self.hasher.verify(text=user_data.password, hashed_text=user.hashed_password):
            raise WrongPasswordError()

        user_session = await self.user_session_gateway.create(user_id=user.id)
        return user_session


class LogoutUser:
    def __init__(self, user_session_gateway: UserSessionGateway):
        self.user_session_gateway = user_session_gateway

    async def execute(self, session_id: str) -> None:
        return await self.user_session_gateway.delete(session_id=UUID(session_id))


class SearchLocation:
    def __init__(self, weather_client: WeatherClient):
        self.weather_client = weather_client

    async def execute(self, location_name: str) -> list[LocationDTO]:
        return await self.weather_client.search_location(name=location_name)


class AddUserLocation:
    def __init__(
        self,
        location_gateway: LocationGateway,
        user_gateway: UserGateway,
        user_session_gateway: UserSessionGateway,
        db_session: DBSession,
    ):
        self.location_gateway = location_gateway
        self.user_gateway = user_gateway
        self.user_session_gateway = user_session_gateway
        self.db_session = db_session

    async def execute(self, session_id: str, location_data: LocationAddInput) -> None:
        user_id = await self.user_session_gateway.get_user_id(session_id=UUID(session_id))
        user = await self.user_gateway.find_by_id(user_id=user_id, load_locations=True)
        if not user:
            raise UserNotFoundError(id=user_id)

        location = await self.location_gateway.get_by_coords(coordinates=location_data.coordinates)

        if location is None:
            location = Location.create(name=location_data.name, coordinates=location_data.coordinates)
            await self.location_gateway.save(location=location)

        try:
            user.add_location(location=location)
            await self.user_gateway.save(user=user)
            await self.db_session.commit()
        except DomainError as e:
            raise UserLocationError(message=e.message)


class RemoveUserLocation:
    def __init__(
        self,
        location_gateway: LocationGateway,
        user_gateway: UserGateway,
        user_session_gateway: UserSessionGateway,
        db_session: DBSession,
    ):
        self.location_gateway = location_gateway
        self.user_gateway = user_gateway
        self.user_session_gateway = user_session_gateway
        self.db_session = db_session

    async def execute(self, session_id: str, location_data: LocationAddInput) -> None:
        user_id = await self.user_session_gateway.get_user_id(session_id=UUID(session_id))
        user = await self.user_gateway.find_by_id(user_id=user_id, load_locations=True)
        if not user:
            raise UserNotFoundError(id=user_id)

        location = await self.location_gateway.get_by_coords(coordinates=location_data.coordinates)
        if not location:
            raise LocationNotFoundError(coordinates=location_data.coordinates)

        try:
            user.remove_location(location=location)
            await self.user_gateway.save(user=user)
            await self.db_session.commit()
        except DomainError as e:
            raise UserLocationError(message=e.message)


class GetUserLocations:
    def __init__(
        self,
        location_gateway: LocationGateway,
        user_gateway: UserGateway,
        user_session_gateway: UserSessionGateway,
        weather_client: WeatherClient,
    ):
        self.location_gateway = location_gateway
        self.user_gateway = user_gateway
        self.user_session_gateway = user_session_gateway
        self.weather_client = weather_client

    async def execute(self, session_id: str) -> list[LocationWeatherDTO]:
        user_id = await self.user_session_gateway.get_user_id(session_id=UUID(session_id))
        user = await self.user_gateway.find_by_id(user_id=user_id, load_locations=True)
        if not user:
            raise UserNotFoundError(id=user_id)

        output = []
        for loc in user.locations:
            weather = await self.weather_client.get_weather_by_location(location=loc)
            output.append(weather)

        return output
