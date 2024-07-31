from typing import TYPE_CHECKING, Optional

from sqlalchemy import select, insert, delete, update

from repositories.base_repository import BaseRepository
from models import Job
from models.contract_jobs import ContractJobs

if TYPE_CHECKING:
    from sqlalchemy import Result


class ContractJobsRepository(BaseRepository):
    async def list_users_with_jobs_contract(
            self, contract_id: int
    ) -> 'Result[tuple[Job, Optional[int]]]':
        stmt = (
            select(Job, ContractJobs.user_id)
            .join(Job, ContractJobs.job_id == Job.id, isouter=True)
            .where(ContractJobs.contract_id == contract_id)
        )
        return await self.session.execute(stmt)

    async def list_jobs_with_and_no_contract(self, contract_id: int) -> 'Result[tuple[int, str, bool, int]]':
        """
        Возвращает комнаты, связанные/не связанные с указанным контрактом
        """
        # Т.к. при обычном join where мы отсеяли бы работы к котором уже привязан какой-либо
        # контракт Было принято решение сделать подзапрос отсеивающий связи в которых
        # не участвует текущий контракт и класть их LEFT OUTER под общее количество работ
        # тем самым мы получаем работы которые не задействованы по отношению к данному контракту
        # и работы которые задействованы к текущему контракту
        sub = (
            select(ContractJobs.job_id, ContractJobs.contract_id)
            .where(ContractJobs.contract_id == contract_id)
            .alias('current_contract_jobs')
        )
        stmt = (
            select(Job.id, Job.name, Job.default, sub.c.contract_id)
            .join(sub, sub.c.job_id == Job.id, isouter=True)
        )
        return await self.session.execute(stmt)

    async def get(
            self,
            contract_id: int,
            job_id: int,
    ) -> 'ContractJobs':
        stmt = (
            select(ContractJobs.id).where(
                ContractJobs.contract_id == contract_id,
                ContractJobs.job_id == job_id
            ).limit(1)
        )
        return await self.session.scalar(stmt)

    async def add_job(self, contract_id: int, job_id: int, user_id: int | None = None) -> 'ContractJobs':
        stmt = insert(ContractJobs).values(
            contract_id=contract_id,
            job_id=job_id,
            user_id=user_id).returning(ContractJobs)

        instance = await self.session.scalar(stmt)
        return instance

    async def edit_job(self, contract_id: int, job_id: int, user_id: int) -> 'ContractJobs':
        stmt = update(ContractJobs).where(
            ContractJobs.contract_id == contract_id,
            ContractJobs.job_id == job_id
        ).values(user_id=user_id).returning(ContractJobs)
        instance = await self.session.scalar(stmt)
        return instance

    async def drop_job(self, contract_id: int, job_id: int) -> 'ContractJobs':
        stmt = delete(ContractJobs).filter_by(
            contract_id=contract_id,
            job_id=job_id).returning(ContractJobs)
        instance = await self.session.scalar(stmt)
        return instance