from typing import List
from app.responses import AivenResponse
from app.project import models


class ProjectListResponse(AivenResponse):
    projects = List[models.ProjectListItem]
