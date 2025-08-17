from unittest.mock import Mock, AsyncMock

import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "Taras",
    "email": "taras@email.com",
    "password": "secret",
    "role": "user",
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Електронна адреса не підтверджена"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": user_data.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_wrong_username_login(client):
    response = client.post(
        "api/auth/login",
        data={"username": "username", "password": user_data.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", data={"password": user_data.get("password")}
    )
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_request_email(client, monkeypatch):
    mock_send_email = AsyncMock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    client.post("api/auth/register", json=user_data)
    response = client.post("api/auth/request_email", json={"email": user_data["email"]})

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Ваша електронна пошта вже підтверджена"


@pytest.mark.asyncio
async def test_confirm_email(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="taras@email.com")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(return_value=Mock(confirmed=False))
    mock_user_service.confirmed_email = AsyncMock(return_value=True)
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirmed_email/token")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Електронну пошту підтверджено"

    mock_get_email_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("taras@email.com")
    mock_user_service.confirmed_email.assert_called_once_with("taras@email.com")


@pytest.mark.asyncio
async def test_confirm_reset_password(client, monkeypatch):
    mock_get_email_from_token = AsyncMock(return_value="taras@email.com")
    mock_get_password_from_token = AsyncMock(return_value="new_hashed_password")
    monkeypatch.setattr("src.api.auth.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr(
        "src.api.auth.get_password_from_token", mock_get_password_from_token
    )

    mock_user_service = Mock()
    mock_user_service.get_user_by_email = AsyncMock(
        return_value=Mock(id=1, email="taras@email.com")
    )
    mock_user_service.reset_password = AsyncMock(return_value=None)
    monkeypatch.setattr("src.api.auth.UserService", lambda db: mock_user_service)

    response = client.get("api/auth/confirm_reset_password/token")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Пароль успішно змінено"

    mock_get_email_from_token.assert_called_once_with("token")
    mock_get_password_from_token.assert_called_once_with("token")
    mock_user_service.get_user_by_email.assert_called_once_with("taras@email.com")
    mock_user_service.reset_password.assert_called_once_with(1, "new_hashed_password")
