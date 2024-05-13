from typing import Optional, TYPE_CHECKING, Type, Callable
import inspect
import logging

from fastapi import HTTPException, status

from repositories import ContractRepository, RoomRepository, JobRepository, TaskRepository, UserRepository
from repositories.base_repository import BaseRepository
from repositories.contract_jobs_repository import ContractJobsRepository
from repositories.contract_rooms_repository import ContractRoomsRepository
from database.connect import session_factory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger()


class SqlAlchemyUnitOfWork:
    def __init__(self, factory: Callable[..., 'AsyncSession'] = session_factory):
        self.factory = factory
        self.session: Optional['AsyncSession'] = None

    async def __aenter__(self):
        self.session = self.factory(expire_on_commit=False)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()
            if exc_type is not HTTPException:
                logger.error(exc_val, exc_type, exc_tb)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='Что-то пошло не так...')
        await self.session.close()

    @property
    def user(self) -> UserRepository:
        return UserRepository(self.session)

    @property
    def contract(self) -> ContractRepository:
        return ContractRepository(self.session)

    @property
    def room(self) -> RoomRepository:
        return RoomRepository(self.session)

    @property
    def job(self) -> JobRepository:
        return JobRepository(self.session)

    @property
    def task(self) -> TaskRepository:
        return TaskRepository(self.session)

    @property
    def contract_jobs(self) -> ContractJobsRepository:
        return ContractJobsRepository(self.session)

    @property
    def contract_rooms(self) -> ContractRoomsRepository:
        return ContractRoomsRepository(self.session)


async def get_unit_of_work() -> 'SqlAlchemyUnitOfWork':
    async with SqlAlchemyUnitOfWork(session_factory) as uow:
        yield uow
