from typing import TYPE_CHECKING

from fastapi import HTTPException, Depends
from starlette import status

from schemas.contract import PublicContractDetail
from service_layer import get_unit_of_work
from schemas.contract_rooms import AddContractRoom, DropContractRoom, PublicContractRooms, SimplePublicRoom
from schemas.room import PublicRoom
from service_layer.contract import get_current_contract

if TYPE_CHECKING:
    from service_layer.unit_of_work import SqlAlchemyUnitOfWork
    from models import Contract

ROOM_ALREADY_CONVICTED_ERROR = 'Данная комната уже привязана к контракту'
CONTRACT_ROOM_RELATION_NOT_EXISTS = 'Связь к которой Вы хотите присоединить пользователя - не существует'


async def list_rooms_with_and_no_contract(
        contract: 'Contract' = Depends(get_current_contract),
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> PublicContractRooms:
    relations = await uow.contract_rooms.list_rooms_with_and_no_contract(contract_id=contract.id)
    no_relations = []
    contract_relations = []
    for room_id, room_name, contract_id in relations:
        room = SimplePublicRoom(id=room_id, name=room_name)
        if contract_id == contract.id:
            contract_relations.append(room)
        else:
            no_relations.append(room)
    return PublicContractRooms(
        contract=PublicContractDetail(
            id=contract.id,
            name=contract.name,
            editable_tasks=contract.editable_tasks
        ),
        contract_relations=contract_relations,
        no_relations=no_relations
    )


async def add_room_to_contract(
        payload: AddContractRoom,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)) -> dict:
    relation = await uow.contract_rooms.get(
        contract_id=payload.contract_id,
        room_id=payload.room_id,
    )
    if relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ROOM_ALREADY_CONVICTED_ERROR
        )
    created = await uow.contract_rooms.add_room(
        contract_id=payload.contract_id,
        room_id=payload.room_id
    )
    if created is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка добавления связи'
        )
    return {'contract_id': created.contract_id, 'room_id': created.room_id}


async def drop_room_from_contract(
        payload: DropContractRoom,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)) -> dict:
    relation = await uow.contract_rooms.get(
        contract_id=payload.contract_id,
        room_id=payload.room_id,
    )
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=CONTRACT_ROOM_RELATION_NOT_EXISTS
        )
    is_dropped = await uow.contract_rooms.drop_room(
        contract_id=payload.contract_id,
        room_id=payload.room_id
    )
    if is_dropped is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка удаления связи'
        )
    return {'contract_id': is_dropped.contract_id, 'room_id': is_dropped.room_id}
