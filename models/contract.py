from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base

if TYPE_CHECKING:
    from models import ContractJobs


class Contract(Base):
    __tablename__ = 'daily_contract'
    name: Mapped[str] = mapped_column(String(15))
    editable_tasks: Mapped[int]

    contract_jobs: Mapped[list['ContractJobs']] = relationship()
