import redis
import pickle
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.db import get_db
from src.database.models import Contact, User
from src.services.contacts import ContactBookService
from src.services.auth import get_current_user
from src.schemas import ContactSet, ContactGet, ContactUpdate

from typing import List


router = APIRouter(prefix="/contacts")
r = redis.Redis(host="localhost", port=6379, db=0)


@router.get("/", response_model=List[ContactGet])
async def get_all_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[Contact]:
    """
    Отримати список всіх контактів.

    Параметри:
    - skip: Кількість записів, які потрібно пропустити (за замовчуванням 0).
    - limit: Максимальна кількість записів, які потрібно повернути (за замовчуванням 100).
    - db: Сесія бази даних.
    - user: Поточний авторизований користувач.

    Повертає:
    - List[Contact]: Список всіх контактів.
    """

    contact_service = ContactBookService(db)
    contacts = await contact_service.get_all_contacts(skip, limit, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactGet)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Contact:
    """
    Отримання інформації про контакт за його ID.

    Параметри:
    - contact_id: ID контакту.
    - db: Сесія бази даних.
    - user: Поточний авторизований користувач.

    Повертає:
    - Contact: Дані контакту.

    Викликає:
    - HTTPException (404): Якщо контакт не знайдено.
    """

    contact = r.get(f"contact:{contact_id}")
    if contact is None:
        contact_service = ContactBookService(db)
        contact = await contact_service.get_contact(contact_id, user)
        r.set(f"contact:{contact_id}", pickle.dumps(contact))
        r.expire(f"contact:{contact_id}", 300)
    else:
        contact = pickle.loads(contact)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactGet, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactSet,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Створення нового контакту.

    Параметри:
    - body: Дані нового контакту.
    - db: Сесія бази даних.
    - user: Поточний авторизований користувач.

    Повертає:
    - Contact: Дані створеного контакту.
    """

    contact_service = ContactBookService(db)
    return await contact_service.create_contact(body, user)


@router.patch("/{contact_id}", response_model_exclude_unset=True)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Оновлення даних контакту за його ID.

    Параметри:
    - body: Нові дані контакту.
    - contact_id: ID контакту.
    - db: Сесія бази даних.
    - user: Поточний авторизований користувач.

    Повертає:
    - Contact: Оновлені дані контакту.

    Викликає:
    - HTTPException (404): Якщо контакт не знайдено.
    """

    contact_service = ContactBookService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}")
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Видалення контакту за його ID.

    Параметри:
    - contact_id: ID контакту.
    - db: Сесія бази даних.
    - user: Поточний авторизований користувач.

    Повертає:
    - Contact: Дані видаленого контакту.

    Викликає:
    - HTTPException (404): Якщо контакт не знайдено.
    """

    contact_service = ContactBookService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get("/birthdays/", response_model=List[ContactGet])
async def get_birthdays(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Отримання списку контактів, які мають день народження протягом наступних 7 днів.

    Параметри:
    - skip: Кількість записів, які потрібно пропустити (за замовчуванням 0).
    - limit: Максимальна кількість записів, які потрібно повернути (за замовчуванням 100).
    - db: Сесія бази даних.
    - user: Поточний авторизований користувач.

    Повертає:
    - List[Contact]: Список контактів із найближчими днями народження.
    """

    bdays = r.get(f"bdays")
    if bdays is None:
        contact_service = ContactBookService(db)
        bdays = await contact_service.get_birthdays(skip, limit, user)
        r.set(f"bdays", pickle.dumps(bdays))
        r.expire(f"bdays", 600)
    else:
        bdays = pickle.loads(bdays)
    return bdays


@router.get("/find/", response_model=List[ContactGet])
async def find_contacts(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Пошук контактів за фільтрами.

    Параметри:
    - query: Пошуковий запит.
    - skip: Кількість записів, які потрібно пропустити (за замовчуванням 0).
    - limit: Максимальна кількість записів, які потрібно повернути (за замовчуванням 100).
    - db: Сесія бази даних.
    - user: Поточний авторизований користувач.

    Повертає:
    - List[Contact]: Список контактів, які відповідають критеріям пошуку.
    """

    contact_service = ContactBookService(db)
    return await contact_service.find_contacts(query, skip, limit, user)
