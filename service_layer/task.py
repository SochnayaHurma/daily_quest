from typing import TYPE_CHECKING, Optional

from fastapi import HTTPException, Depends
from starlette import status

from schemas.user import PublicUser
from service_layer import get_unit_of_work
from schemas import PublicJob
from schemas.task import ToggleTaskStatus, ToggleTaskJob
from service_layer.user import get_current_user

if TYPE_CHECKING:
    from service_layer.unit_of_work import SqlAlchemyUnitOfWork

NOT_EXISTS_TASK_ERROR = 'Данной задачи не существует'
NOT_EXISTS_JOB_ERROR = 'Данной работы не существует'
STATUS_ALREADY_CHANGED_ERROR = 'Статус задачи уже был изменен, пожалуйста обновите страницу'


async def toggle_task_status(
        payload: ToggleTaskStatus,
        current_user: PublicUser = Depends(get_current_user),
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> dict:
    task = await uow.task.get(payload.task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOT_EXISTS_TASK_ERROR
        )
    if task.done == payload.done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=STATUS_ALREADY_CHANGED_ERROR
        )
    user_id = current_user.id if payload.done else None
    is_toggled = await uow.task.toggle_status(task_id=task.id, done=payload.done, user_id=user_id)
    if not is_toggled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка изменения статуса задачи'
        )
    return {'task_id': task.id, 'new_status': payload.done}


async def toggle_task_job(
        payload: ToggleTaskJob,
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> Optional[PublicJob]:
    task = await uow.task.get(payload.task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=NOT_EXISTS_TASK_ERROR
        )
    if task.job == payload.job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=STATUS_ALREADY_CHANGED_ERROR
        )

    if payload.job_id is not None:
        job = await uow.job.get(payload.job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=NOT_EXISTS_JOB_ERROR
            )
        await uow.task.toggle_job(task_id=payload.task_id, job_id=payload.job_id)
        return PublicJob(
            id=job.id,
            name=job.name,
            point=job.point,
            default=job.default,
        )
    else:
        await uow.task.toggle_job(task_id=payload.task_id)
        return None
