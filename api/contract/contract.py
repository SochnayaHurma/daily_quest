from fastapi import Depends, APIRouter
from starlette import status

from schemas.analytics import TaskUserAnalytics
from schemas.contract import PublicContractDetail, PublicContract
from service_layer import analytic, contract

router = APIRouter()


@router.get('/user/task/analytic/')
async def get_user_analytic(
        stats: TaskUserAnalytics = Depends(analytic.get_user_analytic)
) -> TaskUserAnalytics:
    """Возвращает статистику текущего пользователя по выполненным задачам"""
    return stats


@router.get('/list/')
async def list_contracts(
        contracts: list[PublicContractDetail] = Depends(contract.get_list_contracts)
) -> list[PublicContractDetail]:
    """Возвращает список контрактов"""
    return contracts


@router.patch('/edit/')
async def edit_contract(
        contracts: 'PublicContractDetail' = Depends(contract.edit_contract)
) -> 'PublicContractDetail':
    """Редактирует контракт по указанным в теле данным"""
    return contracts

@router.post('/create/',
             status_code=status.HTTP_201_CREATED)
async def create_contract(created_contract: PublicContractDetail = Depends(contract.create_contract)) -> PublicContractDetail:
    """Создает контракт по переданным данным в формате JSON"""
    return created_contract


