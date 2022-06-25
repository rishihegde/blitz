from fastapi import APIRouter

router = APIRouter()

@router.get("/peering")
async def server():
    return {"message": "Creates virtual network peering in the cloud"}