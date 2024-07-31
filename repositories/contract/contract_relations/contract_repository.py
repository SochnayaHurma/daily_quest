from typing import Optional

from sqlalchemy import select, insert, update

from repositories.base_repository import BaseRepository
from models import Contract, ContractRooms


class ContractRepository(BaseRepository):
    async def list(self, ids: Optional[list[int]] = None):
        stmt = select(Contract)
        if ids:
            stmt = stmt.where(Contract.id.in_(ids))
        return await self.session.scalars(stmt)

    async def get(self, contract_id: int) -> "Contract":
        stmt = select(Contract).where(Contract.id == contract_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_name(self, name: str) -> "Contract":
        stmt = select(Contract).where(Contract.name == name).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_name_exclude_author(self, name: str, exclude_name: str) -> "Contract":
        stmt = select(Contract).where(Contract.name == name, Contract.name != exclude_name).limit(1)
        return await self.session.scalar(stmt)

    async def get_last(self) -> "Contract":
        stmt = select(Contract).order_by(Contract.id.desc()).limit(1)
        return await self.session.scalar(stmt)

    async def add_room(self, contract_id: int, room_id: int) -> "ContractRooms":
        stmt = insert(ContractRooms).values(contract_id=contract_id, room_id=room_id).returning(ContractRooms)
        return await self.session.scalar(stmt)

    async def create(self, name: str, editable_tasks: int) -> "Contract":
        stmt = insert(Contract).values(name=name, editable_tasks=editable_tasks).returning(Contract)
        return await self.session.scalar(stmt)

    async def update(self, contract_id: int, **kwargs) -> "Contract":
        stmt = update(Contract).where(Contract.id == contract_id).values(**kwargs).returning(Contract)
        return await self.session.scalar(stmt)
