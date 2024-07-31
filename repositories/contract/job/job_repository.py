from sqlalchemy import select, true, false, insert, and_

from models.contract_jobs import ContractJobs
from repositories.base_repository import BaseRepository
from models import Job


class JobRepository(BaseRepository):
    async def get(self, job_id: int) -> "Job":
        """Возвращает объект работы по имени"""
        stmt = select(Job).where(Job.id == job_id).limit(1)
        return await self.session.scalar(stmt)

    async def get_by_name(self, name: str) -> "Job":
        """Возвращает объект работы по имени"""
        quests_stmt = select(Job).where(Job.name == name)
        return await self.session.scalar(quests_stmt)

    async def list_jobs_by_contract_id(self):
        """
        Возвращает список работ с флагом .default == True
        """
        stmt = select(Job.id, Job)
        result = await self.session.execute(stmt)
        return result.all()

    async def list_default_choice(self, contract_id: int):
        """
        Возвращает список работ с флагом .default == True
        """
        stmt = select(Job.id, Job).join(ContractJobs).where(
            and_(Job.default == true(), ContractJobs.contract_id == contract_id)
        ).group_by(Job.id)
        return list(await self.session.execute(stmt))

    async def list_changeable_jobs(self, contract_id: int):
        stmt = (
            select(Job).join(ContractJobs).where(
                and_(Job.default == false()), ContractJobs.contract_id == contract_id)
        )
        return await self.session.scalars(stmt)

    async def create(self, name: str,
                     point: int,
                     default: bool = False) -> "Job":
        """
        Создает объект в базе данных по схеме указанной в аргументе
        в случае успеха возвращает её представление с дополненными данными базой данных
        """
        stmt = insert(Job).values(name=name,
                                  default=default,
                                  point=point).returning(Job)
        instance = await self.session.scalar(stmt)
        return instance

    async def change_quest_status(self, job_id: int, done: bool = True):
        """
        Если объект с id указанным в аргументе существует
        и аргумент done не равен текущему статусу объект обновляется
        и возвращает обновленное значение
        """
        stmt = select(Job).where(Job.id == job_id)
        quest_instance = await self.session.scalar(stmt)
        if quest_instance and quest_instance.done != done:
            quest_instance.done = done
            return quest_instance
        return None
