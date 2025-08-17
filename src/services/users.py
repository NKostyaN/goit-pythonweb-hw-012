from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Ініціалізація сервісу для роботи з користувачами.

        Аргументи:
            db: Об'єкт асинхронної сесії бази даних.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Створення нового користувача.

        Аргументи:
            body: Дані користувача для створення нового запису.

        Повертає:
            User: Створений користувач.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Отримання користувача за ID.

        Аргументи:
            user_id: ID користувача.

        Повертає:
            User: Знайдений користувач.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Отримання користувача за ім'ям користувача.

        Аргументи:
            username: Ім'я користувача.

        Повертає:
            User: Знайдений користувач.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Отримання користувача за email.

        Аргументи:
            email: Електронна пошта користувача.

        Повертає:
            User: Знайдений користувач.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Підтвердження email користувача.

        Аргументи:
            email: Електронна пошта користувача.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Оновлення URL аватара користувача.

        Аргументи:
            email: Адреса електронної пошти користувача.
            url: Новий URL для аватара.

        Повертає:
            User: Оновлений користувач.
        """
        return await self.repository.update_avatar_url(email, url)

    async def reset_password(self, user_id: int, password: str):
        """
        Скидання пароля користувача.

        Аргументи:
            user_id: ID користувача.
            password: Новий пароль для користувача.

        Повертає:
            User: Оновлений користувач.
        """
        return await self.repository.reset_password(user_id, password)
