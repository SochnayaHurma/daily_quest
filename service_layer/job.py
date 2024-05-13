from typing import TYPE_CHECKING

from fastapi import HTTPException, Depends
from starlette import status

from service_layer import get_unit_of_work
from schemas import PublicJob
from schemas.job import CreateJob
from service_layer.contract import get_current_contract

if TYPE_CHECKING:
    from service_layer.unit_of_work import SqlAlchemyUnitOfWork
    from models import Contract


OUT_OF_DEFAULT_VALUE_ERROR = 'В данном контракте уже достаточно базовых работ: {}'
NOT_EXISTING_CONTRACT_ERROR = 'Указанного контракта не существует'
NAME_ALREADY_EXIST = 'Работа с таким именем уже существует'


async def get_changeable_jobs(
        contract: 'Contract' = Depends(get_current_contract),
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> 'list[PublicJob]':
    jobs = await uow.job.list_changeable_jobs(contract_id=contract.id)
    return [
        PublicJob(
            id=job.id,
            name=job.name,
            point=job.point,
            default=job.default,
        )
        for job in jobs
    ]


async def create_job(
        payload: CreateJob,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> PublicJob:
    if await uow.job.get_by_name(name=payload.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NAME_ALREADY_EXIST
        )
    current_contract = await uow.contract.get(contract_id=payload.contract_id)
    if current_contract is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NOT_EXISTING_CONTRACT_ERROR
        )
    job = await uow.job.create(
        name=payload.name,
        point=payload.point,
        default=payload.default,
    )
    current_contract = await uow.contract.get(contract_id=payload.contract_id)
    await uow.contract_jobs.add_job(contract_id=current_contract.id, job_id=job.id)
    return PublicJob(
        id=job.id,
        name=job.name,
        point=job.point,
        default=job.default,
    )
