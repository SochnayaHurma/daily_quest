from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base, Job, User


class ContractJobs(Base):
    __tablename__ = 'daily_contract_jobs'
    __table_args__ = (
        UniqueConstraint('job_id', 'contract_id'),
    )
    contract_id: Mapped[int] = mapped_column(ForeignKey('daily_contract.id'))
    job_id: Mapped[int] = mapped_column(ForeignKey('daily_job.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('auth_user.id'), nullable=True)

    job: Mapped['Job'] = relationship('Job')
    user: Mapped['User'] = relationship('User')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.contract_id!r}, {self.job_id!r}, {self.user_id!r})'