from typing import Annotated, Optional, TYPE_CHECKING

from fastapi import Depends, HTTPException, Cookie
from starlette import status
from starlette.responses import Response

from config import settings
from service_layer import get_unit_of_work
from schemas.contract import PublicContractDetail, CreateContract, PublicContract, EditContract

if TYPE_CHECKING:
    from service_layer.unit_of_work import SqlAlchemyUnitOfWork
    from models import Contract

NOT_EXISTS_CONTRACT_ERROR = 'Указанного вами контракта не существует'
NOT_FOUND_CONTRACTS = 'Добавьте контракт чтобы начать работу'
NAME_ALREADY_EXIST = 'Контракт с таким именем уже существует'


async def get_current_contract(
        response: Response,
        contract_id: Optional[int] = None,
        cookie_contract_id: Annotated[int | None, Cookie(..., alias=settings.CONTRACT_COOKIE_NAME)] = None,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> 'Contract':
    if contract_id:
        contract = await uow.contract.get(contract_id=contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=NOT_EXISTS_CONTRACT_ERROR
            )
    else:
        if cookie_contract_id:
            contract = await uow.contract.get(contract_id=cookie_contract_id)
        else:
            contract = await uow.contract.get_last()
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=NOT_FOUND_CONTRACTS
            )
    response.set_cookie(settings.CONTRACT_COOKIE_NAME, str(contract.id))
    return contract


async def get_list_contracts(
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work),
        contract: 'Contract' = Depends(get_current_contract)
) -> 'PublicContract':
    current_contract = PublicContractDetail(
        id=contract.id,
        name=contract.name,
        editable_tasks=contract.editable_tasks
    )
    contracts = [PublicContractDetail(
        id=contract.id,
        name=contract.name,
        editable_tasks=contract.editable_tasks
    )
        for contract in await uow.contract.list()]
    return PublicContract(
        current_contract=current_contract,
        contracts=contracts
    )


async def create_contract(
        payload: CreateContract,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> 'PublicContractDetail':
    if await uow.contract.get_by_name(name=payload.name):
        raise HTTPException(
            detail=NAME_ALREADY_EXIST,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    contract = await uow.contract.create(payload.name, payload.editable_tasks)
    if not contract:
        raise HTTPException(
            detail='Ошибка создания контракта',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return PublicContractDetail(
        id=contract.id,
        name=contract.name,
        editable_tasks=contract.editable_tasks
    )


async def edit_contract(
        payload: EditContract,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> 'PublicContractDetail':
    target_contract = await uow.contract.get(payload.id)
    if not target_contract:
        raise HTTPException(
            detail=NOT_EXISTS_CONTRACT_ERROR,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    if await uow.contract.get_by_name_exclude_author(name=payload.name, exclude_name=target_contract.name):
        raise HTTPException(
            detail=NAME_ALREADY_EXIST,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    contract = await uow.contract.update(contract_id=payload.id, name=payload.name, editable_tasks=payload.editable_tasks)

    return PublicContractDetail(
        id=contract.id,
        name=contract.name,
        editable_tasks=contract.editable_tasks
    )
