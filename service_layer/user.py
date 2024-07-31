from typing import Annotated, TYPE_CHECKING

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from service_layer.auth import verify_password, encode_jwt, decode_jwt
from schemas.user import PublicUser, CreateUserSchema
from service_layer import get_unit_of_work

if TYPE_CHECKING:
    from service_layer.unit_of_work import SqlAlchemyUnitOfWork

oauth_schema = OAuth2PasswordBearer(tokenUrl="api/login/")

USER_NOT_EXISTS_ERROR = 'Такого пользователя не существует'
AUTH_ERROR = 'Ошибка входа'
USER_ALREADY_EXISTS_ERROR = 'Пользователь с такими именем/адресом уже существует'
INCORRECT_DATA_ERROR = "Неверные логин или пароль"


async def get_user_by_username_in_body(
        credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
):
    user = await uow.user.get_user(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_EXISTS_ERROR
        )
    return user


async def create_user(
        payload: CreateUserSchema,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work),
):
    user = await uow.user.user_exists(payload.username, payload.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=USER_ALREADY_EXISTS_ERROR
        )
    created_user = await uow.user.create(
        username=payload.username,
        email=payload.email,
        password=payload.password
    )
    return encode_jwt(
        payload={'user_id': created_user.id, 'username': created_user.username}
    )


async def authenticate(
        credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
        user: PublicUser = Depends(get_user_by_username_in_body)
):
    exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=INCORRECT_DATA_ERROR
    )
    if not verify_password(
            plain_password=credentials.password,
            hashed_password=user.password
    ):
        raise exception
    return encode_jwt(payload={
        'user_id': user.id,
        'username': user.username
    })


async def get_current_user(token: str = Depends(oauth_schema),
                           uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)):
    try:
        credentials = decode_jwt(token=token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Forbidden')
    user = await uow.user.get_user(credentials["username"])
    if not user:
        raise HTTPException(
            detail=AUTH_ERROR,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    return PublicUser(
        id=user.id,
        username=user.username,
        email=user.email
    )
