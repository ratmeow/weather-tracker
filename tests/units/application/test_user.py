import uuid
from datetime import UTC, datetime

import pytest

from weather_tracker.application.dto import LoginUserInput, RegisterUserInput, RegisterUserOutput
from weather_tracker.application.exceptions import (
    LoginRequirementError,
    PasswordRequirementError,
    UserAlreadyExistsError,
    UserNotFoundError,
    WrongPasswordError,
)
from weather_tracker.domain.entities import User


@pytest.mark.asyncio
async def test_register_user_success(register_user):
    user_data = RegisterUserInput(login="test", password="strong_password1")

    result = await register_user.execute(user_data=user_data)

    assert isinstance(result, RegisterUserOutput)
    assert result.login == user_data.login
    assert result.hashed_password == "strong_password1"


@pytest.mark.asyncio
async def test_register_user_already_exists(register_user):
    exists_user = User(id=uuid.uuid4(), login="test", hashed_password="other_hashed_password")
    await register_user.user_gateway.save(user=exists_user)

    user_data = RegisterUserInput(login="test", password="strong_password1")

    with pytest.raises(UserAlreadyExistsError):
        await register_user.execute(user_data=user_data)


@pytest.mark.asyncio
async def test_register_user_incorrect_login(register_user):
    invalid_user_data = RegisterUserInput(login="bo", password="strong_password1")
    with pytest.raises(LoginRequirementError):
        await register_user.execute(user_data=invalid_user_data)


@pytest.mark.asyncio
async def test_register_user_incorrect_password(register_user):
    invalid_user_data = RegisterUserInput(login="bob", password="password")

    with pytest.raises(PasswordRequirementError):
        await register_user.execute(user_data=invalid_user_data)


@pytest.mark.asyncio
async def test_login_user_success(login_user):
    exists_user = User(id=uuid.uuid4(), login="test", hashed_password="strong_password1")
    await login_user.user_gateway.save(user=exists_user)

    user_data = LoginUserInput(login="test", password="strong_password1")

    result = await login_user.execute(user_data=user_data)

    assert result.user_id == exists_user.id
    assert result.expired_ts > datetime.now(tz=UTC)


@pytest.mark.asyncio
async def test_login_user_not_found(login_user):
    user_data = LoginUserInput(login="test1", password="strong_password1")

    with pytest.raises(UserNotFoundError):
        await login_user.execute(user_data=user_data)


@pytest.mark.asyncio
async def test_login_wrong_password(login_user):
    exists_user = User(id=uuid.uuid4(), login="test", hashed_password="strong_password1")
    await login_user.user_gateway.save(user=exists_user)

    user_data = LoginUserInput(login="test", password="strong_password2")

    with pytest.raises(WrongPasswordError):
        await login_user.execute(user_data=user_data)
