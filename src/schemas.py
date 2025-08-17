from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from src.database.models import UserRole


class ContactSet(BaseModel):
    """
    Модель для створення контакту.

    Атрибути:
    - first_name: ім'я контакту (максимум 50 символів)
    - last_name: прізвище контакту (максимум 50 символів)
    - email: електронна пошта контакту (максимум 100 символів)
    - phone: номер телефону контакту (максимум 20 символів)
    - birthday: дата народження контакту
    - info: додаткові відомості про контакт (необов'язково)
    """

    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr = Field(max_length=100)
    phone: str = Field(max_length=20)
    birthday: date
    info: Optional[str] = Field(default=None, max_length=200)


class ContactGet(BaseModel):
    """
    Модель для отримання контакту.

    Атрибути:
        id: унікальний ідентифікатор контакту
        first_name: ім'я контакту
        last_name: прізвище контакту
        email: електронна пошта контакту
        phone: номер телефону контакту
        birthday: дата народження контакту
    """

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date

    model_config = ConfigDict(from_attributes=True)


class ContactUpdate(BaseModel):
    """
    Модель для оновлення контакту.

    Атрибути:
        first_name: ім'я контакту (необов'язково)
        last_name: прізвище контакту (необов'язково)
        email: електронна пошта контакту (необов'язково)
        phone: номер телефону контакту (необов'язково)
        birthday: дата народження контакту (необов'язково)
        info: додаткові відомості про контакт (необов'язково)
    """

    first_name: Optional[str] | None = None
    last_name: Optional[str] | None = None
    email: Optional[EmailStr] | None = None
    phone: Optional[str] | None = None
    birthday: Optional[date] | None = None
    info: Optional[str] | None = None


class User(BaseModel):
    """
    Модель для представлення користувача.

    Атрибути:
        id: унікальний ідентифікатор користувача
        username: ім'я користувача
        email: електронна пошта користувача
        avatar: URL до аватара користувача
        role: роль користувача
    """

    id: int
    username: str
    email: str
    avatar: Optional[str] | None = None
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Модель для створення нового користувача.

    Атрибути:
        username: ім'я користувача
        email: електронна пошта користувача
        password: пароль користувача
        role: роль користувача
    """

    username: str
    email: str
    password: str
    role: UserRole


class Token(BaseModel):
    """
    Модель для повернення токену доступу.

    Атрибути:
        access_token: токен доступу
        token_type: тип токену
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Модель для запиту електронної пошти для відновлення паролю.

    Атрибут:
        email: електронна пошта користувача
    """

    email: EmailStr


class ResetPassword(BaseModel):
    """
    Модель для скидання паролю.

    Атрибути:
        email: електронна пошта користувача
        password: новий пароль користувача
    """

    email: EmailStr
    password: str
