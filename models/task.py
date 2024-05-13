from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, func, Integer, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models import Job, Room


class Task(Base):
    __tablename__ = 'daily_task'
    job: Mapped[int] = mapped_column(ForeignKey('daily_job.id'), nullable=True)
    done: Mapped[bool] = mapped_column(default=False, server_default=text('False'))
    room: Mapped[int] = mapped_column(Integer, ForeignKey('daily_room.id'))
    user_committed_id: Mapped[int] = mapped_column(ForeignKey('auth_user.id'), nullable=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey('daily_contract.id'), nullable=False)
    last_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now, server_default=func.now())
    job_item: Mapped['Job'] = relationship(
        'Job',
        back_populates='task'
    )
    room_item: Mapped['Room'] = relationship(
        'Room',
        back_populates='tasks'
    )
