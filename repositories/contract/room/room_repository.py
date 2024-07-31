from typing import Optional, TYPE_CHECKING, Any
from collections import abc
from collections.abc import Sequence

from sqlalchemy import select, insert, func, Integer, text, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import cast

from repositories.base_repository import BaseRepository
from models import Room, Task, ContractRooms, Job

if TYPE_CHECKING:
    from sqlalchemy import Result


class RoomRepository(BaseRepository):
    async def list_rooms_by_contract_id(self, contract_id: int):
        stmt = (
            select(Room)
            .join(ContractRooms, ContractRooms.room_id == Room.id)
            .where(ContractRooms.contract_id == contract_id)
        )
        return await self.session.scalars(stmt)

    async def list_rooms_with_joined_tasks(self, contract_id: int, task_ids: abc.Sequence[int]) -> 'Result[tuple[Room, Any]]':
        """
        Получить список комнат связанных с контрактом.
        Принимает идентификатор контракта.
        Возвращает список комнат связанных с указанным контрактом
        """
        subquery = (
            select(Room.id, func.sum(Job.point * cast(Task.done, Integer)).label('coins'))
            .join(Task, Task.room == Room.id)
            .join(Job, Task.job == Job.id)
            .group_by(Room.id)
            .where(Task.contract_id == contract_id)
        ).alias('done_tasks')
        stmt = (
            select(Room, subquery.c.coins).join(
                ContractRooms,
                ContractRooms.room_id == Room.id
            ).join(subquery, subquery.c.id == Room.id, isouter=True)
            .options(selectinload(Room.tasks.and_(Task.id.in_(task_ids))).joinedload(Task.job_item))
            .where(ContractRooms.contract_id == contract_id)
        )
        return await self.session.execute(stmt)

    async def list_rooms_by_ids_joined(self, ids: Sequence[int]) -> 'list[Room]':
        """
        Получить список комнат связанных с задачами.
        Принимает список идентификаторов задач.
        Возвращает список комнат связанных с данными задачами.
        """
        stmt = (select(Room)
                .join(Room.tasks)
                .join(Task.job_item)
                .where(Task.id.in_(ids))
                )
        return list(await self.session.scalars(stmt))

    async def get_by_name(self, name: str) -> Optional["Room"]:
        """
        Принимает в аргумент имя по которому достается объект Room
        если существует
        """
        stmt = select(Room).where(Room.name == name)
        result = await self.session.scalar(stmt)
        return result

    async def create(self, name: str) -> Optional["Room"]:
        """
        Принимает данные по которым в базе данных создается объект Room
        """
        stmt = insert(Room).values(name=name).returning(Room)
        instance = await self.session.scalar(stmt)
        return instance
