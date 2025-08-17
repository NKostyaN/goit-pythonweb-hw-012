from fastapi import APIRouter, Depends, Request, UploadFile, File

from src.conf.config import settings
from src.database.db import get_db
from src.services.auth import get_current_user, get_current_user_admin
from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.schemas import User

from slowapi import Limiter
from slowapi.util import get_remote_address

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Отримання інформації про поточного авторизованого користувача.

    Обмеження:
    - Не більше 10 запитів на хвилину.

    Параметри:
    - request: HTTP-запит для відстеження ліміту.
    - user: Поточний авторизований користувач.

    Повертає:
    - User: Дані користувача.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Оновлення аватара для поточного адміністратора.

    Параметри:
    - file: Завантажений файл аватара.
    - user: Поточний авторизований адміністратор.
    - db: Сесія бази даних.

    Повертає:
    - User: Оновлені дані користувача з новим URL аватара.
    """
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
