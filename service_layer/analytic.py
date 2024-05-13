from typing import TYPE_CHECKING

from fastapi import Depends

from service_layer import get_unit_of_work
from schemas.analytics import JobUserAnalytics, TaskUserAnalytics
from service_layer.contract import get_current_contract
from service_layer.user import get_current_user

if TYPE_CHECKING:
    from service_layer.unit_of_work import SqlAlchemyUnitOfWork
    from models import Contract
    from schemas.user import PublicUser


async def get_user_analytic(
        contract: 'Contract' = Depends(get_current_contract),
        user: 'PublicUser' = Depends(get_current_user),
        uow: 'SqlAlchemyUnitOfWork' = Depends(get_unit_of_work)
) -> 'TaskUserAnalytics':
    print('tut')
    print('tut')
    print('tut')
    print(contract.id)
    analytic = await uow.task.task_analytics(contract_id=contract.id, user_id=user.id)
    user_stat = TaskUserAnalytics()
    for job in analytic:  # type: dict
        job_id = job.get('job_id')
        job_name = job.get('job_name')
        task_done = job.get('task_done', 0)
        task_not_done = job.get('task_not_done', 0)
        coin_accepted = job.get('coin_accepted', 0)
        coin_could_be = job.get('coin_could_be', 0)

        user_stat.task_done += task_done
        user_stat.task_not_done += task_not_done
        user_stat.coin_accepted += coin_accepted
        user_stat.coin_could_be += coin_could_be
        user_stat.jobs.add(
            JobUserAnalytics(
                job_id=job_id,
                job_name=job_name,
                task_done=task_done,
                task_not_done=task_not_done,
                coin_accepted=coin_accepted,
                coin_could_be=coin_could_be
            )
        )
    return user_stat
