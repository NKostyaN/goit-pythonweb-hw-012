from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
)
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail, ResetPassword
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    get_password_from_token,
)
from src.services.users import UserService
from src.services.email import send_email, send_reset_password_email
from src.database.db import get_db


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Реєстрація нового користувача.

    Параметри:
    - user_data: Дані нового користувача.
    - background_tasks: Об'єкт для виконання фонових задач.
    - request: Запит для отримання базового URL.
    - db: Сесія бази даних.

    Повертає:
    - User: Дані зареєстрованого користувача, або HTTPException (409), якщо користувач з таким email вже існує.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Авторизація користувача.

    Параметри:
    - form_data: Дані для авторизації.
    - db: Сесія бази даних.

    Повертає:
    - Token: JWT токен доступу, або HTTPException (401), якщо логін або пароль неправильний, або не підтверджений email.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Підтвердження email користувача.

    Параметри:
    - token: Токен підтвердження.
    - db: Сесія бази даних.

    Повертає:
    - dict: Повідомлення про успішне підтвердження, повідомлення якщо пошта вже підтверджена, або HTTPException (400), якщо токен недійсний або користувача не знайдено.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Надсилання підтвердження email користувачу.

    Параметри:
    - body: Дані для запиту.
    - background_tasks: Об'єкт для виконання фонових задач.
    - request: Запит для отримання базового URL.
    - db: Сесія бази даних.

    Повертає:
    - dict: Повідомлення про надісланий запит, або повідомлення якщо пошта вже підтверджена.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.post("/reset_password")
async def reset_password_request(
    body: ResetPassword,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Запит на скидання пароля.

    Параметри:
    - body: Дані для запиту.
    - background_tasks: Об'єкт для виконання фонових задач.
    - request: Запит для отримання базового URL.
    - db: Сесія бази даних.

    Повертає:
    - dict: Повідомлення про надісланий запит, або HTTPException (400), якщо email не підтверджений.
    """

    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if not user:
        return {"message": "Перевірте свою електронну пошту для підтвердження"}
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ваша електронна пошта не підтверджена",
        )
    hashed_password = Hash().get_password_hash(body.password)
    reset_token = await create_access_token(
        data={"sub": user.email, "password": hashed_password}
    )
    background_tasks.add_task(
        send_reset_password_email,
        email=body.email,
        username=user.username,
        host=str(request.base_url),
        reset_token=reset_token,
    )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.get("/confirm_reset_password/{token}")
async def confirm_reset_password(token: str, db: Session = Depends(get_db)):
    """
    Підтвердження скидання пароля.

    Параметри:
    - token: Токен підтвердження скидання пароля.
    - db: Сесія бази даних.

    Повертає:
    - dict: Повідомлення про успішне скидання пароля, HTTPException (400), якщо токен недійсний, або HTTPException (404), якщо користувача не знайдено.
    """

    email = await get_email_from_token(token)
    hashed_password = await get_password_from_token(token)
    if not email or not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недійсний або прострочений токен",
        )
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача з такою електронною адресою не знайдено",
        )
    await user_service.reset_password(user.id, hashed_password)
    return {"message": "Пароль успішно змінено"}
