from collections import abc
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from fastapi import Depends, HTTPException
from starlette import status

from schemas.contract import PublicContractDetail
from schemas.utils import create_room_schema_with_tasks
from service_layer import get_unit_of_work
from models import Task, Room, Job
from schemas import PublicJob
from service_layer.contract import get_current_contract
from service_layer.utils import get_current_time_interval
from schemas.room import PublicRoom, PublicTask, CreateRoom

if TYPE_CHECKING:
    from models import Contract
    from service_layer.unit_of_work import SqlAlchemyUnitOfWork

ROOM_ALREADY_EXISTS_ERROR = 'Комната с таким именем уже существует'


def make_task_prepend_save_db(
        *,
        contract_id: int, room: 'Room', job: Optional['Job'] = None
) -> dict:
    job_id = job.id if job else None
    return {
        'contract_id': contract_id,
        'room': room.id,
        'job': job_id,
        'last_date': datetime.now()
    }


async def create_tasks_for_rooms(
        rooms: abc.Iterable[Room],
        jobs: abc.Iterable[Job],
        contract: 'Contract',
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
):
    tasks = []
    for room in rooms:
        for job in jobs:
            dict_task = make_task_prepend_save_db(contract_id=contract.id, job=job, room=room)
            tasks.append(dict_task)
        if contract.editable_tasks > 0:
            tasks.extend(
                make_task_prepend_save_db(contract_id=contract.id, room=room)
                for _ in range(contract.editable_tasks)
            )
    return await uow.task.create_mass(tasks)


async def get_rooms_with_joined_tasks(
        tasks_ids: list[int],
        contract: 'Contract' = Depends(get_current_contract),
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> 'list[PublicRoom]':
    rooms_with_tasks = await uow.room.list_rooms_with_joined_tasks(
        contract_id=contract.id,
        task_ids=tasks_ids
    )
    schemas_room = []
    for room, coins in rooms_with_tasks:  # type: (Room, int)
        tasks = []
        for task in room.tasks:  # type: Task
            if task.job_item:
                job = PublicJob(
                    id=task.job_item.id,
                    name=task.job_item.name,
                    point=task.job_item.point,
                    default=task.job_item.default,
                )
            else:
                job = None
            tasks.append(PublicTask(
                id=task.id,
                done=task.done,
                contract_id=contract.id,
                job=job
            ))
        schemas_room.append(PublicRoom(
            id=room.id,
            name=room.name,
            coins=coins if coins else 0,
            tasks=tasks
        ))
    return schemas_room


async def give_today_room_tasks(
        contract: 'Contract' = Depends(get_current_contract),
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
):
    start, end = get_current_time_interval()

    tasks_ids = await uow.task.list_ids(start, end, contract.id)
    if len(tasks_ids) == 0:
        rooms = list(await uow.room.list_rooms_by_contract_id(contract.id))
        jobs = dict(await uow.job.list_default_choice(contract_id=contract.id))

        if len(rooms) == 0 or len(jobs) == 0:
            return {
                'rooms': [],
                'contract': PublicContractDetail(
                    id=contract.id,
                    name=contract.name,
                    editable_tasks=contract.editable_tasks
                )
            }
        tasks: list[tuple[int, Task]] = await create_tasks_for_rooms(rooms, jobs.values(), contract, uow)
        tasks_ids = (task[0] for task in tasks)
    return {
        'rooms': await get_rooms_with_joined_tasks(tasks_ids, contract, uow),
        'contract': PublicContractDetail(
            id=contract.id,
            name=contract.name,
            editable_tasks=contract.editable_tasks
        )
    }


async def create_room(
        payload: CreateRoom,
        contract: 'Contract' = Depends(get_current_contract),
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> 'PublicRoom':
    if await uow.room.get_by_name(name=payload.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ROOM_ALREADY_EXISTS_ERROR
        )
    room = await uow.room.create(name=payload.name)
    await uow.contract_rooms.add_room(contract_id=payload.contract_id, room_id=room.id)
    jobs: dict[int, Job] = dict(await uow.job.list_default_choice(contract.id))
    if len(jobs) > 0:
        tasks = await create_tasks_for_rooms(
            rooms=(room,),
            jobs=jobs.values(),
            contract=contract,
            uow=uow
        )
    else:
        tasks = []
    return create_room_schema_with_tasks(room, jobs, tasks, contract)
