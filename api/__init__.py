__all__ = (
    'contract_router',
    'auth_router',
    'router'
)

from fastapi import APIRouter

from api.contract import router as contract_router
from api.auth import router as auth_router


router = APIRouter(prefix='/api', tags=['API_v1'])
router.include_router(contract_router)
router.include_router(auth_router)
