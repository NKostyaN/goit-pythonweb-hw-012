import pytest

from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1,
        username="testuser",
        email="test@email.com",
        avatar="https://test.com/ava.png",
        role="user",
    )


@pytest.fixture
def user_data():
    return UserCreate(
        username="testuser",
        email="test@email.com",
        password="secret",
        role="user",
    )


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_id(1)

    assert result == user
    mock_session.execute.assert_called_once()
    mock_session.execute.return_value.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_username("testuser")

    assert result == user
    mock_session.execute.assert_called_once()
    mock_session.execute.return_value.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_email("test@email.com")

    assert result == user
    mock_session.execute.assert_called_once()
    mock_session.execute.return_value.scalar_one_or_none.assert_called_once()


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session, user, user_data):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user

    result = await user_repository.create_user(
        user_data,
        avatar="https://test.com/ava.png",
    )

    assert result.username == user.username
    assert result.email == user.email
    assert result.avatar == user.avatar
    assert result.role == user.role

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session, user):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user))
    )
    user.confirmed = False

    await user_repository.confirmed_email(user.email)

    assert user.confirmed is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session, user):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user))
    )
    new_avatar_url = "https://test.com/new_ava.png"

    result = await user_repository.update_avatar_url(user.email, new_avatar_url)

    assert result.avatar == new_avatar_url
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_reset_password(user_repository, mock_session, user):
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user))
    )
    new_password = "new_password"

    result = await user_repository.reset_password(user.id, new_password)

    assert result.hashed_password == new_password
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)
