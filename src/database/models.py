from datetime import datetime

from enum import Enum
from sqlalchemy import String, ForeignKey, func, Enum as SqlEnum
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.sql.sqltypes import DateTime, Boolean


class Base(DeclarativeBase):
    """Базовий клас для опису всіх моделей."""

    pass


class Contact(Base):
    """
    Модель для таблиці contacts.

    Атрибути:
    - id: Первинний ключ з автозбільшенням.
    - first_name: Ім'я контакту (обов'язкове), максимум 50 символів.
    - last_name: Прізвище контакту (обов'язкове), максимум 50 символів.
    - email: Електронна пошта контакту (обов'язкова), максимум 100 символів.
    - phone: Телефонний номер контакту (обов'язковий), максимум 20 символів.
    - birthday: Дата народження контакту (обов'язкова).
    - info: Додаткова інформація про контакт (опціональна).
    - user_id: Зовнішній ключ для прив'язки до користувача.
    - user: Відношення до моделі User.
    """

    __tablename__ = "contact_book"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    info: Mapped[str] = mapped_column(String(200), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship("User", backref="contact_book")


class UserRole(str, Enum):
    """
    Список ролей користувачів.

    Значення:
    - USER: Звичайний користувач.
    - ADMIN: Адміністратор.
    """

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    Модель для таблиці users.

    Атрибути:
    - id: Первинний ключ.
    - username: Ім'я користувача (обов'язкове, унікальне), максимум 50 символів.
    - email: Електронна пошта користувача (обов'язкова, унікальна), максимум 100 символів.
    - hashed_password: Зашифрований пароль (обов'язкове).
    - created_at: Дата створення запису (автоматично).
    - avatar: URL-адреса аватара користувача (обов'язкове).
    - confirmed: Стан підтвердження користувача.
    - role: Роль користувача (USER або ADMIN).
    """

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed = mapped_column(Boolean, default=False)
    role = mapped_column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
