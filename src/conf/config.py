from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Клас конфігурації для налаштувань додатка.

    Атрибути:
    - DB_URL: URL для підключення до бази даних.
    - JWT_SECRET: Секретний ключ для підпису JWT-токенів.
    - JWT_ALGORITHM: Алгоритм для генерації JWT-токенів (за замовчуванням: 'HS256').
    - JWT_EXPIRATION_SECONDS: Час життя токенів у секундах (за замовчуванням: 3600).
    - MAIL_USERNAME: Логін для SMTP сервера.
    - MAIL_PASSWORD: Пароль для SMTP сервера.
    - MAIL_FROM: Електронна адреса, від якої надсилаються листи.
    - MAIL_PORT: Порт для підключення до SMTP сервера (за замовчуванням: 465).
    - MAIL_SERVER: Доменне ім'я SMTP сервера (за замовчуванням: 'smtp.meta.ua').
    - MAIL_FROM_NAME: Ім'я відправника для листів (за замовчуванням: 'Rest API Service').
    - MAIL_STARTTLS: Чи використовувати STARTTLS для SMTP (за замовчуванням: False).
    - MAIL_SSL_TLS: Чи використовувати SSL/TLS для SMTP (за замовчуванням: True).
    - USE_CREDENTIALS: Чи використовувати облікові дані для SMTP (за замовчуванням: True).
    - VALIDATE_CERTS: Чи перевіряти сертифікати SSL (за замовчуванням: True).
    - CLOUDINARY_NAME: Ім'я облікового запису Cloudinary.
    - CLOUDINARY_API_KEY: API-ключ для Cloudinary.
    - CLOUDINARY_API_SECRET: Секретний ключ для Cloudinary.

    Методи:
    - model_config: Конфігурація для завантаження налаштувань із файлу '.env'.
    """

    DB_URL: str = ""
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr = "user@mail.com"
    MAIL_PASSWORD: str = ""
    MAIL_FROM: EmailStr = "user@mail.com"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLOUDINARY_NAME: str = ""
    CLOUDINARY_API_KEY: int = 0
    CLOUDINARY_API_SECRET: str = ""

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
