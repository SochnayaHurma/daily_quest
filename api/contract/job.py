from fastapi import Depends, APIRouter
from starlette import status

from schemas import PublicJob
from schemas.contract_jobs import PublicUserContractJobs
from service_layer import contract_jobs, job

router = APIRouter(
    tags=['Job'],
    prefix='/job',
)

@router.get('/users/')
async def list_user_relation_to_contract_jobs(
        jobs: PublicUserContractJobs = Depends(contract_jobs.list_user_contract_jobs)
) -> PublicUserContractJobs:
    """Возвращает список работ, доступных для текущего контракта"""
    return jobs

@router.get('/list/')
async def list_contract_jobs(
        jobs = Depends(contract_jobs.list_jobs_with_and_no_contract)
):
    """Возвращает список работ связанных с текущим контрактом"""
    return jobs


@router.get('/choices/')
async def list_job_choices(
        jobs: list[PublicJob] = Depends(job.get_changeable_jobs)
) -> list[PublicJob]:
    """Возвращает список работ, доступных для выбора в текущем контракте"""
    return jobs


@router.post('/create/',
             status_code=status.HTTP_201_CREATED)
async def create_job(created_job: PublicJob = Depends(job.create_job)) -> PublicJob:
    """Создает работу по переданным данным в формате JSON"""
    return created_job

@router.post('/add/')
async def add_job_to_contract(
        relation: dict[str, int | None] = Depends(contract_jobs.add_job_to_contract)
) -> dict[str, int | None]:
    """Порождает связь работы с контрактом указанных в теле запроса"""
    return relation


@router.post('/drop/')
async def drop_job_to_contract(
        relation: dict[str, int | None] = Depends(contract_jobs.drop_job_from_contract)
) -> dict[str, int | None]:
    """Удаляет связь работы с контрактом указанных в теле запроса"""
    return relation


@router.patch('/edit/user/')
async def edit_user_to_job_contract(
        relation: dict[str, int | None] = Depends(contract_jobs.edit_user_to_job_contract)
) -> dict[str, int | None]:
    """Привязывает пользователя к работе по указанным идентификаторам"""
    return relation
