import json
from typing import Dict, Union
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, ValidationError, validator
from app.core.helper import helper
from app import crud, schemas

router = APIRouter()

class Network(BaseModel):
    """ Pydantic model for Network

    Attributes:
        name: str
            name of the network
        description: str
            (optional) description of the network
        region: str
            region where the network should be created, default is ap-south-1
        cidr: str
            cidr of the network, default is 10.0.0.0/16
        private_subnet_size: int
            private subnet size - supported are 18, 21, 24, default is 21 supporting 2048 hosts
        public_subnet_size: int
            public subnet size - supported are 18, 21, 24, default is 24 supporting 256 hosts
        azs: list
            list of availability zones where the network, default is ["a","b","c"]
        enable_nat_gateway: bool
            (optional) enable nat gateway, default is false
    """
    name: str
    description: Union[str, None] = None
    region: str = 'ap-south-1'
    cidr: str = '10.0.0.0/16'
    private_subnet_size: int = 21
    public_subnet_size: int = 24
    azs: list = ['a', 'b', 'c']
    enable_nat_gateway: bool = False

    # @validator('mask')
    # def supported_mask_values(cls, v):
    #     """Validate mask value
    #     """
    #     if v not in [18, 21, 24]:
    #         raise ValueError('must contain supported subnet masks: 18, 21 or 24')
    #     return v.__str__()

@router.delete("/network/{name}")
def delete_network(name: str, db: Session = Depends(helper.get_db)) -> json:
    """Delete a network by name 

    Arguments:
        name (str): Name of the network
        db (Session): Database session
    
    Returns:
        json: Success or failure message in json response
    
    """
    vnetwork = crud.get_network(db, name)
    if vnetwork:
        helper.debug(f'Deleting network {name}')
        helper.delete_network(vnetwork.__dict__)
        crud.delete_network(db, name)
        return {"message": f"Network {name} deleted"}
    else:
        helper.debug(f'Network {name} not found')
        return {"message": f"Network {name} not found"}

@router.post("/network")
def create_network(network: Network, db: Session = Depends(helper.get_db)) -> json:
    """Create a network using the given parameters in the request body
    
    Arguments:
        network (Network): Network object
        db (Session): Database session
    
    Returns:
        json: Success, failure, resource locked message in json response

    """

    try:
        # create resource lock
        crud.acquire_resource_lock(db, schemas.Locks(name=network.name))

        # check if network already exists
        if crud.get_network(db, network.name):
            crud.release_resource_lock(db, schemas.Locks(name=network.name))
            return {"message": f"Network {network.name} already exists"}
        
        # create network if does not exist
        vnetwork = helper.create_network(network.json())
        n = schemas.NetworksCreate(name=network.name, vpc_id=vnetwork['vpc_id'], tf_state=vnetwork['state'], payload=network.dict())
        crud.create_network(db, n)

        # return result
        crud.release_resource_lock(db, schemas.Locks(name=network.name))
        return {"message": f"Network {network.name} created"}
    except IntegrityError:
        return {"message": f"Network {network.name} is locked"}
    except Exception as e:
        # release resource lock
        crud.release_resource_lock(db, schemas.Locks(name=network.name))
        return {"message": f"Network {network.name} creation failed: {e}"}

@router.get("/network/{name}")
def get_network(name: str, db: Session = Depends(helper.get_db)) -> dict:
    """Get a network by name
    
    Arguments:
        name (str): Name of the network
        db (Session): Database session

    Returns:
        dict: Network object as dictionary

    """
    a = crud.get_network(db=db, network_name=name)
    if a :
        b = a.__dict__
        helper.debug(f'Deleting network {name}')
        return b
    else:
        helper.debug(f'Network {name} not found')
        return {"message": f"Network {name} does not exist"}