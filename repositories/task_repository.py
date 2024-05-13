from datetime import datetime

from sqlalchemy import select, insert, update, and_, func, Integer, cast, RowMapping, between, ScalarResult
from sqlalchemy.sql import null

from repositories.base_repository import BaseRepository
from models import Task, Job, ContractJobs


class TaskRepository(BaseRepository):
    async def list_ids(
            self,
            start: datetime,
            end: datetime,
            contract_id: int
    ) -> 'list[int]':
        stmt = (
            select(Task.id, Task)
            .where(Task.contract_id == contract_id)
            .where(and_(
                Task.last_date > start, Task.last_date < end
            ))
        )
        return list(await self.session.scalars(stmt))

    async def get(self, task_id: int) -> 'Task':
        stmt = select(Task).where(Task.id == task_id).limit(1)
        return await self.session.scalar(stmt)

    async def create_mass(self, tasks: 'list[dict]'):
        stmt = insert(Task).values(tasks).returning(Task.id, Task)
        tasks = await self.session.execute(stmt)
        return tasks

    async def toggle_status(self, task_id: int, done: bool, user_id: int):
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(done=done, user_committed_id=user_id)
        ).returning(Task.id)
        result = await self.session.execute(stmt)
        return result

    async def toggle_job(self, task_id: int, job_id: int | None = None):
        if job_id is None:
            job_id = null()
        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(job=job_id)
        ).returning(Task.id)
        result = await self.session.execute(stmt)
        return result

    async def task_analytics(self, contract_id: int, user_id: int) -> list[RowMapping]:
        stmt = (
            select(
                func.sum(cast(Task.done, Integer)).label('task_done'),
                func.sum(cast(~Task.done, Integer)).label('task_not_done'),
                func.sum(cast(Task.done, Integer) * Job.point).label('coin_accepted'),
                func.sum(Job.point).label('coin_could_be'),
                Job.id.label('job_id'),
                Job.name.label('job_name')
            )
            .join(ContractJobs, ContractJobs.job_id == Task.job)
            .join(Job, Job.id == Task.job)
            .group_by(Job.id)
            .where(
                ContractJobs.user_id == user_id,
                ContractJobs.contract_id == contract_id,
                Task.contract_id == contract_id
            )
        )
        result = await self.session.execute(stmt)
        return list(result.mappings())
