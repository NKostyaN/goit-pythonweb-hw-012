import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactBookRepository
from src.schemas import ContactSet


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactBookRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser", role="user")


@pytest.fixture
def contact(user: User):
    return Contact(
        id=1,
        first_name="Taras",
        last_name="Shevchenko",
        email="taras.shevchenko@email.com",
        phone="380-111-1111",
        birthday="1814-03-09",
        user=user,
    )


@pytest.fixture
def contact_data():
    return ContactSet(
        first_name="Taras",
        last_name="Shevchenko",
        email="taras.shevchenko@email.com",
        phone="380-111-1111",
        birthday="1814-03-09",
    )


@pytest.mark.asyncio
async def test_get_all_contacts(contact_repository, mock_session, user, contact):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_all_contacts(skip=0, limit=10, user=user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "Taras"


@pytest.mark.asyncio
async def test_get_contact(contact_repository, mock_session, user, contact):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    resault = await contact_repository.get_contact(contact_id=1, user=user)

    assert resault is not None
    assert resault.id == 1
    assert resault.first_name == "Taras"


@pytest.mark.asyncio
async def test_create_contact(
    contact_repository, mock_session, user, contact, contact_data
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.create_contact(body=contact_data, user=user)

    assert isinstance(result, Contact)
    assert result.first_name == "Taras"


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user, contact):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(contact_id=1, user=user)

    assert result is not None
    assert result.first_name == "Taras"
    assert result.email == "taras.shevchenko@email.com"
    mock_session.delete.assert_awaited_once_with(contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_contact(
    contact_repository, mock_session, user, contact, contact_data
):
    contact_data.first_name = "John"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    assert result is not None
    assert result.first_name == "John"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact)


@pytest.mark.asyncio
async def test_find_contacts(contact_repository, mock_session, user, contact):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.find_contacts(
        query="Taras", skip=0, limit=10, user=user
    )

    assert len(result) == 1
    assert result[0].first_name == "Taras"
