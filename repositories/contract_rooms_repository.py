from typing import TYPE_CHECKING, Optional

from sqlalchemy import select, insert, delete

from repositories.base_repository import BaseRepository
from models import ContractRooms, Room
from models.contract_jobs import ContractJobs

if TYPE_CHECKING:
    from sqlalchemy import Result


class ContractRoomsRepository(BaseRepository):

    async def list_rooms_with_and_no_contract(self, contract_id: int) -> 'Result[tuple[int, str, int]]':
        """
        Возвращает комнаты, связанные/не связанные с указанным контрактом
        """
        # Т.к. при обычном join where мы отсеяли бы работы к котором уже привязан какой-либо
        # контракт Было принято решение сделать подзапрос отсеивающий связи в которых
        # не участвует текущий контракт и класть их LEFT OUTER под общее количество работ
        # тем самым мы получаем работы которые не задействованы по отношению к данному контракту
        # и работы которые задействованы к текущему контракту
        sub = (
            select(ContractRooms.room_id, ContractRooms.contract_id)
            .where(ContractRooms.contract_id == contract_id)
            .alias('current_contract_jobs')
        )
        stmt = (
            select(Room.id, Room.name, sub.c.contract_id)
            .join(sub, sub.c.room_id == Room.id, isouter=True)
        )
        return await self.session.execute(stmt)

    async def list_rooms_with_contracts(self) -> 'Result[tuple[Room, Optional[int]]]':
        stmt = (
            select(Room, ContractRooms.contract_id)
            .join(Room, ContractRooms.room_id == Room.id, isouter=True)
        )
        return await self.session.execute(stmt)

    async def get(
            self,
            contract_id: int,
            room_id: int,
    ) -> 'ContractJobs':
        stmt = (
            select(ContractRooms.id).where(
                ContractRooms.contract_id == contract_id,
                ContractRooms.room_id == room_id
            ).limit(1)
        )
        return await self.session.scalar(stmt)

    async def add_room(self, contract_id: int, room_id: int) -> 'ContractRooms':
        stmt = insert(ContractRooms).values(
            contract_id=contract_id,
            room_id=room_id).returning(ContractRooms)
        instance = await self.session.scalar(stmt)
        return instance

    async def drop_room(self, contract_id: int, room_id: int) -> 'ContractRooms':
        stmt = delete(ContractRooms).filter_by(
            contract_id=contract_id,
            room_id=room_id).returning(ContractRooms)
        instance = await self.session.scalar(stmt)
        return instance
