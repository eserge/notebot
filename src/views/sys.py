from typing import Dict

from fastapi import APIRouter

sys_router = APIRouter()


@sys_router.get("/healthcheck/")
async def healthcheck() -> Dict:
    return {"healthcheck": "OK"}
