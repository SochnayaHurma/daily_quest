from fastapi import Depends, APIRouter
from starlette import status

from schemas import PublicJob
from schemas.analytics import TaskUserAnalytics
from schemas.contract import PublicContractDetail, PublicContract
from schemas.contract_jobs import PublicUserContractJobs
from schemas.contract_rooms import PublicContractRooms
from schemas.room import PublicRoom
from service_layer import task, contract_jobs, contract_rooms, analytic, contract, job, room
# from service_layer.user import get_current_user

router = APIRouter(
    tags=['Daily Quest'],
    prefix='/contract',
    # dependencies=[Depends(get_current_user)]
)


@router.get('/room/list/task/')
async def list_rooms_with_tasks(
        rooms: dict = Depends(room.give_today_room_tasks)
) -> dict:
    """Возвращает список комнат с задачами по указанному в куки контракту"""
    return rooms


@router.get('/user/task/analytic/')
async def get_user_analytic(
        stats: TaskUserAnalytics = Depends(analytic.get_user_analytic)
) -> TaskUserAnalytics:
    """Возвращает статистику текущего пользователя по выполненным задачам"""
    return stats


@router.get('/job/users/')
async def list_user_relation_to_contract_jobs(
        jobs: PublicUserContractJobs = Depends(contract_jobs.list_user_contract_jobs)
) -> PublicUserContractJobs:
    """Возвращает список работ, доступных для текущего контракта"""
    return jobs

@router.get('/job/list/')
async def list_contract_jobs(
        jobs = Depends(contract_jobs.list_jobs_with_and_no_contract)
):
    """Возвращает список работ связанных с текущим контрактом"""
    return jobs

@router.get('/room/list/')
async def list_contract_rooms(
        rooms: 'PublicContractRooms' = Depends(contract_rooms.list_rooms_with_and_no_contract)
) -> 'PublicContractRooms':
    """Возвращает список комнат связанных с текущим контрактом"""
    return rooms


@router.get('/job/choices/')
async def list_job_choices(
        jobs: list[PublicJob] = Depends(job.get_changeable_jobs)
) -> list[PublicJob]:
    """Возвращает список работ, доступных для выбора в текущем контракте"""
    return jobs


@router.get('/list/')
async def list_contracts(
        contracts: 'PublicContract' = Depends(contract.get_list_contracts)
) -> 'PublicContract':
    """Возвращает список контрактов"""
    return contracts


@router.patch('/edit/')
async def edit_contract(
        contracts: 'PublicContractDetail' = Depends(contract.edit_contract)
) -> 'PublicContractDetail':
    """Редактирует контракт по указанным в теле данным"""
    return contracts


@router.post('/job/create/',
             status_code=status.HTTP_201_CREATED)
async def create_job(created_job: PublicJob = Depends(job.create_job)) -> PublicJob:
    """Создает работу по переданным данным в формате JSON"""
    return created_job


@router.post('/create/',
             status_code=status.HTTP_201_CREATED)
async def create_contract(created_contract: PublicContractDetail = Depends(contract.create_contract)) -> PublicContractDetail:
    """Создает контракт по переданным данным в формате JSON"""
    return created_contract


@router.post('/room/create/')
async def create_room(created_room: PublicRoom = Depends(room.create_room)) -> PublicRoom:
    """
    Создает комнату по переданным данным в формате JSON
        и генерирует пустые задачи на текущий день.
    Возвращает комнату с пустыми задачами
    """
    return created_room


@router.patch('/task/toggle/done/')
async def toggle_task_status(new_status: dict[str, bool] = Depends(task.toggle_task_status)) -> dict:
    """Меняет статус задачи исходя из данных переданных в теле запроса"""
    return new_status


@router.patch(
    '/task/toggle/job/',
)
async def change_task_quest(new_job: PublicJob | None = Depends(task.toggle_task_job)) -> PublicJob | None:
    """Меняет выполняемую работу на текущей задаче"""
    return new_job


@router.post('/job/add/')
async def add_job_to_contract(
        relation: dict[str, int | None] = Depends(contract_jobs.add_job_to_contract)
) -> dict[str, int | None]:
    """Порождает связь работы с контрактом указанных в теле запроса"""
    return relation


@router.post('/job/drop/')
async def drop_job_to_contract(
        relation: dict[str, int | None] = Depends(contract_jobs.drop_job_from_contract)
) -> dict[str, int | None]:
    """Удаляет связь работы с контрактом указанных в теле запроса"""
    return relation


@router.patch('/job/edit/user/')
async def edit_user_to_job_contract(
        relation: dict[str, int | None] = Depends(contract_jobs.edit_user_to_job_contract)
) -> dict[str, int | None]:
    """Привязывает пользователя к работе по указанным идентификаторам"""
    return relation


@router.post('/room/add/')
async def add_room_to_contract(
        relation: dict[str, int] = Depends(contract_rooms.add_room_to_contract)
) -> dict[str, int]:
    """Привязывает комнату к контракту указанному в теле запроса"""
    return relation


@router.post('/room/drop/')
async def drop_room_to_contract(
        relation: dict[str, int] = Depends(contract_rooms.drop_room_from_contract)
) -> dict[str, int]:
    """Отвязывает комнату от контракта по указанным данным в теле запроса"""
    return relation
