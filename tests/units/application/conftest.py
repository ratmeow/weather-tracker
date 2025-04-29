import pytest

from weather_tracker.application.use_cases import (
    AddUserLocation,
    GetUserLocations,
    LoginUser,
    LogoutUser,
    RegisterUser,
    RemoveUserLocation,
    SearchLocation,
)

from .mocks import (
    MockDBSession,
    MockHasher,
    MockLocationGateway,
    MockUserGateway,
    MockUserSessionGateway,
    MockWeatherClient,
)


@pytest.fixture
def user_gateway():
    return MockUserGateway()


@pytest.fixture
def user_session_gateway():
    return MockUserSessionGateway()


@pytest.fixture
def db_session():
    return MockDBSession()


@pytest.fixture(scope="module")
def hasher():
    return MockHasher()


@pytest.fixture
def location_gateway():
    return MockLocationGateway()


@pytest.fixture(scope="module")
def weather_client():
    return MockWeatherClient()


@pytest.fixture
def register_user(user_gateway, hasher, db_session):
    return RegisterUser(user_gateway=user_gateway, hasher=hasher, db_session=db_session)


@pytest.fixture
def login_user(user_gateway, hasher, user_session_gateway):
    return LoginUser(user_gateway=user_gateway, hasher=hasher, user_session_gateway=user_session_gateway)


@pytest.fixture
def logout_user(user_session_gateway):
    return LogoutUser(user_session_gateway=user_session_gateway)


@pytest.fixture
def add_user_location(user_gateway, location_gateway, db_session, user_session_gateway):
    return AddUserLocation(
        user_gateway=user_gateway,
        location_gateway=location_gateway,
        user_session_gateway=user_session_gateway,
        db_session=db_session,
    )


@pytest.fixture
def remove_user_location(user_gateway, location_gateway, db_session, user_session_gateway):
    return RemoveUserLocation(
        user_gateway=user_gateway,
        location_gateway=location_gateway,
        db_session=db_session,
        user_session_gateway=user_session_gateway,
    )


@pytest.fixture
def get_user_locations(user_gateway, location_gateway, weather_client, user_session_gateway):
    return GetUserLocations(
        user_gateway=user_gateway,
        location_gateway=location_gateway,
        weather_client=weather_client,
        user_session_gateway=user_session_gateway,
    )


@pytest.fixture
def search_location(weather_client):
    return SearchLocation(weather_client=weather_client)
