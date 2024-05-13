from collections.abc import Sequence
from typing import Optional

from sqlalchemy import select, Row, or_

from repositories.base_repository import BaseRepository
from auth import hash_password
from models import User
from schemas.user import PublicUser


class UserRepository(BaseRepository):
    async def get_user(self, username: str) -> Optional[User]:
        """Извлекает из базы данных пользователя"""
        stmt = select(User).where(User.username == username)
        user = await self.session.scalar(stmt)
        if user:
            return user
        return None

    async def get_user_list(self) -> 'Sequence[Row[tuple[int, User]]]':
        """Извлекает всех пользователей из таблицы auth_user"""
        result = await self.session.execute(select(User.id, User))
        return result.all()

    async def user_exists(self, username: str, email: str) -> bool:
        """Проверяет пользователя на существование"""
        stmt = select(User.id).where(or_(
            User.username == username,
            User.email == email
        ))
        user = await self.session.scalar(stmt)
        return user

    async def create(
            self,
            username: str,
            email: str,
            password: str
    ) -> PublicUser:
        """Создает пользователя в базе данных"""
        hashed_password = hash_password(password)
        user = User(
            username=username,
            password=hashed_password,
            email=email
        )
        self.session.add(user)
        instance = PublicUser(
            username=user.username,
            email=user.email,
        )
        await self.session.commit()
        return instance
