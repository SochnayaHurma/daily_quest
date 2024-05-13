
from collections import abc
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import Depends

from service_layer import get_unit_of_work
from models import Task, Room, Job
from schemas import PublicJob
from service_layer.contract import get_current_contract
from schemas.room import PublicRoom, PublicTask

if TYPE_CHECKING:
    from models import Contract
    from service_layer.unit_of_work import SqlAlchemyUnitOfWork

ROOM_ALREADY_EXISTS_ERROR = 'Комната с таким именем уже существует'


def make_task_prepend_save_db(
        *,
        contract_id: int, room: 'Room', job: 'Job'
) -> dict:
    return {
        'contract_id': contract_id,
        'room': room.id,
        'job': job.id,
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
            tasks.append(PublicTask(
                id=task.id,
                done=task.done,
                contract_id=contract.id,
                job=PublicJob(
                    id=task.job_item.id,
                    name=task.job_item.name,
                    point=task.job_item.point,
                    default=task.job_item.default,
                )
            ))
        schemas_room.append(PublicRoom(
            id=room.id,
            name=room.name,
            coins=coins,
            tasks=tasks
        ))
    return schemas_room


def create_room_schema_with_tasks(
        room: 'Room',
        jobs: 'dict[int, Job]',
        tasks: 'dict[int, Task]',
        contract: 'Contract'
) -> 'PublicRoom':
    room_tasks = []
    for task_id, task_obj in tasks:
        if task_obj.job:
            job = PublicJob(
                id=jobs[task_obj.job].id,
                name=jobs[task_obj.job].name,
                point=jobs[task_obj.job].point,
                default=jobs[task_obj.job].default,
            )
        else:
            job = None
        room_tasks.append(PublicTask(
            id=task_id,
            done=task_obj.done,
            contract_id=contract.id,
            job=job
        ))
    return PublicRoom(
        id=room.id,
        name=room.name,
        tasks=room_tasks
    )
