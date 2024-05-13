from datetime import datetime, timedelta

from fastapi import HTTPException, status
import jwt
import bcrypt

from config import settings


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(
        password=plain_password.encode(),
        salt=bcrypt.gensalt()
    ).decode()


def verify_password(
        plain_password: str | bytes,
        hashed_password: str | bytes
) -> bool:
    return bcrypt.checkpw(
        plain_password.encode(),
        hashed_password.encode()
    )


def encode_jwt(
        payload: dict[str, str | int],
        secret_key: str = settings.SECRET_KEY,
        expire_minutes: int = settings.TOKEN_EXPIRE_MINUTES
):
    iat = datetime.utcnow()
    exp = iat + timedelta(minutes=expire_minutes)
    to_encode = payload.copy()
    to_encode['iat'] = iat
    to_encode['exp'] = exp
    return jwt.encode(
        payload=to_encode,
        key=secret_key,
        algorithm='HS256'
    )


def decode_jwt(
        token: str | bytes,
        secret_key: str = settings.SECRET_KEY,
):
    return jwt.decode(
        jwt=token,
        key=secret_key,
        algorithms=settings.TOKEN_ALGORITHM
    )
