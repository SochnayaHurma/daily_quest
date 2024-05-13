from typing import TYPE_CHECKING

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models import ContractJobs


class User(Base):
    __tablename__ = 'auth_user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    social_id: Mapped[str] = mapped_column(String(255), nullable=True)

    jobs: Mapped[list['ContractJobs']] = relationship(back_populates='user')
