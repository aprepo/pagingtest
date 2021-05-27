from pydantic import BaseModel, AnyUrl
from typing import List, Optional
import basic_types as types


class AivenResponse(BaseModel):
    nav: types.AivenNavi


class AivenIndexResponse(AivenResponse):
    service_types: AnyUrl


class ServiceTypeListResponse(AivenResponse):
    service_types: List[types.ServiceTypeListItem]
