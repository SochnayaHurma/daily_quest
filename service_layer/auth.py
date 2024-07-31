from datetime import datetime, timedelta

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
        secret_key: str = settings.auth.SECRET_KEY,
        expire_minutes: int = settings.auth.TOKEN_EXPIRE_MINUTES
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
        secret_key: str = settings.auth.SECRET_KEY,
):
    return jwt.decode(
        jwt=token,
        key=secret_key,
        algorithms=settings.auth.TOKEN_ALGORITHM
    )
