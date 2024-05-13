from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from models.task import Task


class Room(Base):
    __tablename__ = 'daily_room'
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    tasks: Mapped[list["Task"]] = relationship('Task', order_by='Task.id')
