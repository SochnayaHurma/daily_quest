from typing import TYPE_CHECKING

from fastapi import HTTPException, Depends
from starlette import status

from database.connect import session_factory
from schemas.contract import PublicContractDetail
from schemas.user import PublicUser
from service_layer import get_unit_of_work
from schemas import PublicJob
from schemas.contract_jobs import AddContractJob, DropContractJob, AddUserToContractJob, PublicUserContractJobs, \
    SimplePublicJob, UserJobRelation, PublicContractJobs
from service_layer.contract import get_current_contract

if TYPE_CHECKING:
    from service_layer.unit_of_work import SqlAlchemyUnitOfWork
    from models import Contract

JOB_IS_ALREADY_CONVICTED = 'Данное задание уже привязано к контракту'
CONTRACT_JOB_RELATION_NOT_EXISTS = 'Связь к которой Вы хотите присоединить пользователя - не существует'


async def list_user_contract_jobs(
        contract: 'Contract' = Depends(get_current_contract),
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> PublicUserContractJobs:
    relations = await uow.contract_jobs.list_users_with_jobs_contract(contract_id=contract.id)
    users = dict(await uow.user.get_user_list())
    no_relations = []
    user_relations = {
        user_id: UserJobRelation(user_id=user_id, username=user.username)
        for user_id, user in users.items()
    }
    for job_object, user_id in relations:
        job = SimplePublicJob(id=job_object.id, name=job_object.name, default=job_object.default)
        if user_id:
            user_relations[user_id].jobs.append(job)
        else:
            no_relations.append(job)
    return PublicUserContractJobs(
        contract=PublicContractDetail( # TODO нужен ли тут контракт
            id=contract.id,
            name=contract.name,
            editable_tasks=contract.editable_tasks
        ),
        user_relations=user_relations,
        no_relations=no_relations
    )


async def list_jobs_with_and_no_contract(
        contract: 'Contract' = Depends(get_current_contract),
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> PublicContractJobs:
    relations = await uow.contract_jobs.list_jobs_with_and_no_contract(contract_id=contract.id)
    no_relations = []
    contract_relations = []
    for job_id, job_name, is_default, contract_id in relations:
        job = SimplePublicJob(id=job_id, name=job_name, default=is_default)
        if contract_id:
            contract_relations.append(job)
        else:
            no_relations.append(job)
    return PublicContractJobs(
        contract=PublicContractDetail(
            id=contract.id,
            name=contract.name,
            editable_tasks=contract.editable_tasks
        ),
        contract_relations=contract_relations,
        no_relations=no_relations
    )


async def add_job_to_contract( # TODO нужно ли генерировать таски на сегодняшний
                                # TODO день при добавлении дефолтной работы к контракту
        payload: AddContractJob,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)) -> dict:
    job = await uow.job.get(payload.job_id)
    contract = await uow.contract.get(payload.contract_id)
    if not job or not contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    relation = await uow.contract_jobs.get(
        contract_id=payload.contract_id,
        job_id=payload.job_id,
    )
    if relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=JOB_IS_ALREADY_CONVICTED
        )
    created = await uow.contract_jobs.add_job(
        contract_id=payload.contract_id,
        job_id=payload.job_id,
        user_id=payload.user_id
    )
    if created is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка добавления связи'
        )
    return {'contract_id': created.contract_id, 'job_id': created.job_id, 'user_id': created.user_id}


async def drop_job_from_contract(
        payload: DropContractJob,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)) -> dict:
    relation = await uow.contract_jobs.get(
        contract_id=payload.contract_id,
        job_id=payload.job_id,
    )
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CONTRACT_JOB_RELATION_NOT_EXISTS
        )
    is_dropped = await uow.contract_jobs.drop_job(
        contract_id=payload.contract_id,
        job_id=payload.job_id
    )
    if is_dropped is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка удаления связи'
        )
    return {'contract_id': is_dropped.contract_id, 'job_id': is_dropped.job_id, 'user_id': is_dropped.user_id}


async def edit_user_to_job_contract(
        payload: AddUserToContractJob,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)) -> dict:
    relation = await uow.contract_jobs.get(
        contract_id=payload.contract_id,
        job_id=payload.job_id,
    )
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CONTRACT_JOB_RELATION_NOT_EXISTS
        )
    edited = await uow.contract_jobs.edit_job(
        contract_id=payload.contract_id,
        job_id=payload.job_id,
        user_id=payload.user_id
    )
    if edited is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка взаимодействия с группой'
        )
    return {'user_id': edited.user_id, 'contract_id': edited.contract_id, 'job_id': edited.job_id}
