from fastapi import Depends, APIRouter

from schemas.contract_rooms import PublicContractRooms
from schemas.room import PublicRoom
from service_layer import contract_rooms, room

router = APIRouter(
    prefix='/root',
    tags=['Room']
)


@router.get('/list/task/')
async def list_rooms_with_tasks(
        rooms: dict = Depends(room.give_today_room_tasks)
) -> dict:
    """Возвращает список комнат с задачами по указанному в куки контракту"""
    return rooms


@router.get('/list/')
async def list_contract_rooms(
        rooms: 'PublicContractRooms' = Depends(contract_rooms.list_rooms_with_and_no_contract)
) -> 'PublicContractRooms':
    """Возвращает список комнат связанных с текущим контрактом"""
    return rooms


@router.post('/create/')
async def create_room(created_room: PublicRoom = Depends(room.create_room)) -> PublicRoom:
    """
    Создает комнату по переданным данным в формате JSON
        и генерирует пустые задачи на текущий день.
    Возвращает комнату с пустыми задачами
    """
    return created_room

@router.post('/add/')
async def add_room_to_contract(
        relation: dict[str, int] = Depends(contract_rooms.add_room_to_contract)
) -> dict[str, int]:
    """Привязывает комнату к контракту указанному в теле запроса"""
    return relation


@router.post('/drop/')
async def drop_room_to_contract(
        relation: dict[str, int] = Depends(contract_rooms.drop_room_from_contract)
) -> dict[str, int]:
    """Отвязывает комнату от контракта по указанным данным в теле запроса"""
    return relation
