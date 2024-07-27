from dataclasses import dataclass

from fastapi import APIRouter, Depends, Response, status

from service_layer.user import create_user, authenticate, get_current_user
from schemas.token import AccessToken
from schemas.user import PublicUser

router = APIRouter(tags=['Authenticate'])


@dataclass
class Settings:
    access_cookie_key: str = 'access_token'
    cookie_max_age: int = 350


settings = Settings()


@router.post('/register/', status_code=status.HTTP_201_CREATED)
async def register(token: str = Depends(create_user)):
    return AccessToken(access_token=token)


@router.post('/login/')
async def login(token: str = Depends(authenticate)):
    return AccessToken(access_token=token)


@router.post('/logout/', status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie('access_token')


@router.get('/with/me/')
async def get_current_user(user: PublicUser = Depends(get_current_user)):
    return user
