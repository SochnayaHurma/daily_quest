__all__ = (
    'contract_router',
    'auth_router',
    'router'
)

from fastapi import APIRouter

from api.contract.contract import router as contract_router
from api.contract.job import router as job_router
from api.contract.room import router as room_router
from api.contract.task import router as task_router
from api.user.auth import router as auth_router

router = APIRouter(
    tags=['Daily Quest'],
    prefix='/contract',
)
router.include_router(contract_router)
router.include_router(job_router)
router.include_router(room_router)
router.include_router(task_router)
router.include_router(auth_router)
