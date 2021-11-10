from pydantic import BaseModel, AnyUrl, Field
from typing import Any, List, Optional
from app import basic_types as types
from app.aiven import projects


class AivenResponse(BaseModel):
    nav: types.AivenNavi


class AivenIndexResponse(AivenResponse):
    pass


class ServiceTypeListResponse(AivenResponse):
    from_cache: bool
    service_types: List[types.ServiceTypeListItem]


class ProjectList(BaseModel):
    from_cache: bool
    projects: List[types.ProjectListItem]


class ProjectListResponse(BaseModel):
    nav: types.AivenNavi
    from_cache: bool
    projects: ProjectList
    #projects: List[types.ProjectListItem]


class ApiStatsResponse(BaseModel):
    private_cache_sessions: int = Field(description="Size of the internal cache (sessions)")
    private_cache_responses: int = Field(description="Count of individual responses in the cache")