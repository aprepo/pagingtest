from fastapi import APIRouter
from app.project import responses
from app.project import views


router = APIRouter()


@router.get("/projects", response_model=responses.ProjectListResponse)
def projects():
    return views.project_list()
