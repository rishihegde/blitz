from fastapi import APIRouter

router = APIRouter()

@router.get("/server")
async def server():
    return {"message": "Hello World"}

@router.get("/servers")
async def servers(limit: int = 10):
    message = f'Listing {limit} servers'
    return {"message": message}