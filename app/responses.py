from pydantic import BaseModel, AnyUrl
from typing import List, Optional
from app import basic_types as types


class AivenResponse(BaseModel):
    nav: types.AivenNavi

    class Config:
        arbitrary_types_allowed = True


class AivenIndexResponse(AivenResponse):
    service_types: AnyUrl


class ServiceTypeListResponse(AivenResponse):
    service_types: List[types.ServiceTypeListItem]
