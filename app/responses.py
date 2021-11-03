from pydantic import BaseModel, AnyUrl
from typing import List, Optional
from app import basic_types as types


class AivenResponse(BaseModel):
    nav: types.AivenNavi


class AivenIndexResponse(AivenResponse):
    pass


class ServiceTypeListResponse(AivenResponse):
    from_cache: bool
    service_types: List[types.ServiceTypeListItem]
