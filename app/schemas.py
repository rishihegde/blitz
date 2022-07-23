import json
from typing import Union
from pydantic import BaseModel

class NetworksBase(BaseModel):
    name: str
    vpc_id: str
    plan_id: Union[int, None]
    plan_state: Union[str, None]
    tf_state: str
    payload: dict

class NetworksCreate(NetworksBase):
    pass

class Networks(NetworksBase):
    id: int

class Locks(BaseModel):
    name: str
    
    class Config:
        orm_mode = True