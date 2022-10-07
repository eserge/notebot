from fastapi import APIRouter

from views.auth import auth_router
from views.sys import sys_router

router = APIRouter()
router.include_router(sys_router)
router.include_router(auth_router)
