from fastapi import Depends, APIRouter

from schemas import PublicJob
from service_layer import task

router = APIRouter(prefix='/task', tags=['Task'])

@router.patch('/toggle/done/')
async def toggle_task_status(new_status: dict[str, bool] = Depends(task.toggle_task_status)) -> dict:
    """Меняет статус задачи исходя из данных переданных в теле запроса"""
    return new_status


@router.patch(
    '/toggle/job/',
)
async def change_task_quest(new_job: PublicJob | None = Depends(task.toggle_task_job)) -> PublicJob | None:
    """Меняет выполняемую работу на текущей задаче"""
    return new_job
