from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models import Room


class ContractRooms(Base):
    __tablename__ = 'daily_contract_rooms'
    __table_args__ = (
        UniqueConstraint('room_id', 'contract_id'),
    )
    contract_id: Mapped[int] = mapped_column(ForeignKey('daily_contract.id'))
    room_id: Mapped[int] = mapped_column(ForeignKey('daily_room.id'))

    room: Mapped['Room'] = relationship('Room')


