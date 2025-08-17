from typing import List
from datetime import date, timedelta

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactSet, ContactUpdate


class ContactBookRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_all_contacts(
        self, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Отримання списку всіх контактів.

        Параметри:
        - skip: Кількість записів, які потрібно пропустити.
        - limit: Максимальна кількість записів, які потрібно повернути.
        - user: Поточний авторизований користувач.

        Повертає:
        - List[Contact]: Список всіх контактів.
        """

        res = await self.db.execute(
            select(Contact).filter_by(user=user).offset(skip).limit(limit)
        )
        return res.scalars().all()

    async def get_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Отримання інформації про контакт за його ID.

        Параметри:
        - contact_id: ID контакту.
        - user: Поточний авторизований користувач.

        Повертає:
        - Contact: Дані контакту.
        """

        res = await self.db.execute(select(Contact).filter_by(id=contact_id, user=user))
        return res.scalar_one_or_none()

    async def create_contact(self, body: ContactSet, user: User) -> Contact:
        """
        Створення нового контакту.

        Параметри:
        - body: Дані нового контакту.
        - user: Поточний авторизований користувач.

        Повертає:
        - Contact: Дані створеного контакту.
        """

        contact = Contact(**body.model_dump(), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Видалення контакту за його ID.

        Параметри:
        - contact_id: ID контакту.
        - user: Поточний авторизований користувач.

        Повертає:
        - Contact: Дані видаленого контакту.
        """

        contact = await self.get_contact(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> Contact | None:
        """
        Оновлення даних контакту за його ID.

        Параметри:
        - contact_id: ID контакту.
        - body: Нові дані контакту.
        - user: Поточний авторизований користувач.

        Повертає:
        - Contact: Оновлені дані контакту.
        """

        contact = await self.get_contact(contact_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def get_birthdays(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Отримання списку контактів, які мають день народження протягом наступних 7 днів.

        Параметри:
        - skip: Кількість записів, які потрібно пропустити.
        - limit: Максимальна кількість записів, які потрібно повернути.
        - user: Поточний авторизований користувач.

        Повертає:
        - List[Contact]: Список контактів із найближчими днями народження.
        """

        today = date.today()
        nextweek = today + timedelta(days=7)
        contacts = await self.get_all_contacts(skip, limit, user)
        res = []
        for contact in contacts:
            bday = contact.birthday.replace(year=today.year).date()
            if bday >= today and bday <= nextweek:
                res.append(contact)
        return res

    async def find_contacts(self, query: str, skip: int, limit: int, user: User):
        """
        Пошук контактів за фільтрами.

        Параметри:
        - query: Пошуковий запит.
        - skip: Кількість записів, які потрібно пропустити.
        - limit: Максимальна кількість записів, які потрібно повернути.
        - user: Поточний авторизований користувач.

        Повертає:
        - List[Contact]: Список контактів, які відповідають критеріям пошуку.
        """

        result = await self.db.execute(
            select(Contact)
            .filter_by(user=user)
            .where(
                or_(
                    Contact.first_name.ilike(f"%{query}%"),
                    Contact.last_name.ilike(f"%{query}%"),
                    Contact.email.ilike(f"%{query}%"),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
