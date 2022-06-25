from typing import Union
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.helper import helper

router = APIRouter()

class Network(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    region: str
    cidr: str
    azs: list
    enable_nat_gateway: bool = False

@router.post("/network/{name}")
async def create_network(name: str, network: Network):
    vnet = helper.parse_json(network.json())
    return {"message": f"Network {name} created with {vnet['cidr']}"}

@router.get("/network")
async def server(name: Union[str, None] = None):
    return {"message": "Gets virtual networks in the cloud or only one network provided in ?name="}