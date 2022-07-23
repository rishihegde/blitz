from fastapi import APIRouter
from typing import Union
from app.core.config import settings
from app.core.helper import helper

router = APIRouter()

@router.post("/tf")
async def tf(state: Union[str, None] = 'local', 
            bucket_region: Union[str, None] = settings.DEFAULT_AWS_REGION, 
            bucket_name: Union[str, None] = settings.DEFAULT_S3_BUCKET, 
            bucket_key: Union[str, None] = settings.DEFAULT_S3_KEY,
            ):
    return helper.terraform_variables(state, bucket_region, bucket_name, bucket_key)
