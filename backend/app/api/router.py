from fastapi import APIRouter

from app.api.endpoints import admin, auth, disputes, operator_cases


router = APIRouter(prefix="/api/v1")
router.include_router(disputes.router)
router.include_router(operator_cases.router)
router.include_router(auth.router)
router.include_router(admin.router)
