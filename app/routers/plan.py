from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()


@router.get("/plan/{plan_id}")
async def plan(plan_id: int):
    return {"plan_id": plan_id}


