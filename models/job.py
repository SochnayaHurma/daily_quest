from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base


class Job(Base):
    __tablename__ = 'daily_job'
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    point: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    default: Mapped[bool] = mapped_column(server_default='False', default=False)
    task = relationship('Task')
