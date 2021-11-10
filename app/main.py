from os import environ as env, stat
from collections import OrderedDict
from itertools import islice

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request
import uvicorn
import logging
from app import aiven
from app import basic_types as types
from app import responses
from app import models
from app.aiven import accounts as _accounts, cache, projects as _projects, services as _services
from app.settings import BASEURL

logger = logging.getLogger("myapp")

response_codes = {
    404: {"description": "Item not found"},
    302: {"description": "The item was moved"},
    403: {"description": "Not enough privileges"},
}

tags_metadata = [
    {
        "name": "Service",
        "description": "<p>Basic unit of Aiven ecosystem is Service.</p>"
                       "<p>The service is a runtime instance of a service plan, basically a database cluster. "
                       "Depending on the plan, the service can consist of one or more different nodes, ie. virtual "
                       "machines.</p>"
                       "<p>"
                       "</p>"
    },
    {
        "name": "Service type",
        "description": "<p>Aiven supports multiple types of services. Each service type has multiple levels of plans "
                       "with different sets of resources and pricing.</p>"
                       "<p>Some types of services support multiple versions, others are offered by Aiven as the current"
                       "version basis, where Aiven will always make sure the service is following the latest stable and"
                       "best version available.</p>"
    },
    {
        "name": "Project",
        "description": "Project description goes here"
    },
    {
        "name": "Kafka",
        "description": "Kafka service details"
    },
    {
        "name": "API stats",
        "description": "Statiscics and metrics of the API itself, such as size of cache."
    }
]
app = FastAPI(
    title="Aiven API", version="RC-2.0",
    openapi_tags=tags_metadata,
    description="<p>McDonalds version (ie. not serious draft) of the possible way to split the Aiven API.</p>"
                "<p>Original API docs at: <a href='https://api.aiven.io/doc/'>https://api.aiven.io/doc/</a></p>"
                "<p>Target to improve in this proposal:"
                "<ul>"
                "<li>Split the Service to smaller sets of data</li>"
                "<li>New Service List endpoint that returns links to more detailed Service endpoints</li>"
                "<li>HATEOAS approach: provide links to other endpoints where approperiate</li>"
                "</ul>"
)


MAIN_NAVI = {
    'docs': f"{BASEURL}{app.docs_url}",
    'redoc': f"{BASEURL}/redoc",
    'home': f"{BASEURL}/",
    "service_types": f"{BASEURL}/service_types",
    "accounts": f"{BASEURL}/accounts",
    "projects": f"{BASEURL}/projects",
    "services": f"{BASEURL}/services",
}


def _get_token(request: Request):
    token = request.headers.get('authorization', None)
    if token:
        return token
    else:
        raise HTTPException(status_code=403, detail="No BEARER token")


@app.get("/", response_model=responses.AivenIndexResponse)
def index():
    return {
        "nav": MAIN_NAVI,
        "service_types": f"{BASEURL}/service_types",
        "projects": f"{BASEURL}/projects",
    }

@app.get("/api/stats", response_model=responses.ApiStatsResponse, tags=['API stats'])
def api_stats(request: Request): 
    return {
        "private_cache_sessions": cache.get_cache_session_count(),
        "private_cache_responses": cache.get_cache_response_count()
    }


@app.get("/service_types", response_model=responses.ServiceTypeListResponse, tags=["Service type"])
def service_types():
    service_types, from_cache = _services.get_service_types()
    return {
        "nav": MAIN_NAVI,
        "from_cache": from_cache,
        'service_types': [
            {'name': key, 'url': f"{BASEURL}/service_types/{key}"} for key in service_types["service_types"].keys()
        ]
    }


@app.get("/service_types/{service_type}", responses=response_codes, tags=["Service type"])
def service_type(service_type: types.ServiceType):
    service_types, from_cache = _services.get_service_types()
    service_types = service_types.get('service_types', {})
    if service_type.value in service_types:
        properties = service_types.get(service_type.value)
    else:
        raise Exception(f"Unknown service type: {service_type.value}")
    _plans_base_url = f"{BASEURL}/service_types/{service_type.value}/service_plans/"
    return {
        "nav": MAIN_NAVI,
        "from_cache": from_cache,
        "service_type": {
            "name": service_type.value,
            "description": properties.get("description"),
            "versions" : {
                "latest_available_version": properties.get("latest_available_version"),
                "default_version": properties.get("default_version"),
                "all_versions": f"{BASEURL}/service_types/{service_type.value}/versions"
            },
            "plans": {
                "url": _plans_base_url,
                "shortcuts": {
                    plan.get("service_plan") : {
                        "url": f"{_plans_base_url}{plan.get('service_plan')}/"
                    }
                    for plan in properties.get("service_plans")
                }
            },
        },
    }


@app.get("/service_types/{service_type}/versions", responses=response_codes, tags=["Service type"])
def service_type_versions(service_type):
    return {
        "nav": MAIN_NAVI,
        "service_type": {
            "name": service_type,
            "url": f"{BASEURL}/service_types/{service_type}/"
        },
        "versions": _services.get_service_versions(service_type)
    }


@app.get("/service_types/{service_type}/service_plans", responses=response_codes, tags=["Service type"])
def service_type_plans(service_type):
    service_types, from_cache = _services.get_service_types()
    service_types = service_types.get('service_types', {})
    plans = {
        "nav": MAIN_NAVI,
        "from_cache": from_cache,
        'service_type': {
            'name': service_type,
            'url': f"{BASEURL}/service_types/{service_type}"
        },
        'plans': [
            {
                'plan': plan.get('service_plan'),
                'url': f"{BASEURL}/service_types/{service_type}/service_plans/{plan.get('service_plan')}"
            }
            for plan in service_types.get(service_type).get('service_plans') if plan.get('service_plan') != plan
        ]
    }
    return plans


@app.get("/service_types/{service_type}/service_plans/{plan}", responses=response_codes, tags=["Service type"])
def service_type_plan(service_type, plan):
    service_types, from_cache = _services.get_service_types()
    service_types = service_types.get('service_types', {})
    plans = [p for p in service_types.get(service_type).get('service_plans') if p.get('service_plan') == plan]
    assert len(plans) == 1
    return {
        "nav": MAIN_NAVI,
        "from_cache": from_cache,
        'service_type': {
            'name': service_type,
            'url': f"{BASEURL}/service_types/{service_type}"
        },
        "all_plans": {
            "url": f"{BASEURL}/service_types/{service_type}/service_plans"
        },
        "plan": plans.pop()
    }


@app.get("/service_types/{service_type}/service_plans/{plan}/regions", responses=response_codes, tags=["Service plan"])
def service_plan_regions(service_type, plan, order_by="name", filter: str = None, page: int = None, paginate_by: int = None):
    if paginate_by:
        if page is None or int(page) < 1:
            page = 1

    url = f"{BASEURL}/service_types/{service_type}/service_plans/{plan}/regions?"

    FIELDS = {"id", "disk_space_mb", "price_usd", "node_memory_mb"}
    service_types, from_cache = _services.get_service_types()
    service_types = service_types.get('service_types', {})
    _service_plans = service_types.get(service_type).get('service_plans', {})
    p = _find_plan(_service_plans, plan)

    regions: dict = p.get("regions", dict())
    num_regions = len(regions)
    region_keys = [k for k in regions.keys()]

    # Filter
    for region in regions:
        pass

    # Order
    ordered_list = OrderedDict()
    region_keys.sort()      # TODO proper sorting
    for k in region_keys:
        ordered_list[k] = regions.get(k)

    # Paginate
    if paginate_by:
        def chunks(data):
            it = iter(data)
            for i in range(0, len(data), paginate_by):
                yield {k:data[k] for k in islice(it, paginate_by)}

        paginated = [item for item in chunks(ordered_list)]
        ordered_list = paginated[page]

        meta_pagination = {
            "is_paginated": True,
            "paginate_by": paginate_by,
            "page": page,
            "num_pages": len(paginated),
            "total_items": num_regions,
            "prev": pagelink(url, paginate_by, page - 1),
            "next": pagelink(url, paginate_by, page + 1),
        }
    else:
        meta_pagination = {
            "is_paginated": False,
            "total_items": num_regions,
        }

    return {
        "meta": {
            "navi": {
                "all_plans": f"{BASEURL}/service_types/{service_type}/service_plans",
                "this_plan": f"{BASEURL}/service_types/{service_type}/service_plans/{plan}",
            },
            "filtering": {
                "is_filtered": filter is not None,
                "filter": filter
            },
            "ordering": {
                "is_ordered": True,
                "order_by": order_by,  # todo multiple values
            },
            "pagination": meta_pagination,
        },
        "data" : ordered_list
    }


@app.get("/projects", response_model=responses.ProjectListResponse, responses=response_codes, tags=["Project"])
def projects_list(request: Request):
    token = _get_token(request)
    try:
        projects, from_cache = _projects.get_projects(token=token)
        return { 
            "nav": MAIN_NAVI,
            "from_cache": from_cache,
            "projects": projects,
            }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.get("/project/{project}", response_model=models.Project, responses=response_codes, tags=["Project"])
def project():
    return models.Project()

@app.get("/accounts/", responses=response_codes, tags=["Account"])
def accounts(request: Request):
    token = _get_token(request)
    try:
        accounts, from_cache = _accounts.get_accounts(token)
        return {
            'nav': MAIN_NAVI,
            'from_cache': from_cache,
            'accounts': accounts,
        } 
    except Exception as e:
        #raise HTTPException(status_code=500, detail=str(e))
        raise e


@app.get("/accounts/{account_id}/", responses=response_codes, tags=["Account"])
def account(account_id: str, request: Request):
    token = _get_token(request)
    try:
        account, from_cache = _accounts.get_account(token, account_id)
        return {
            'nav': MAIN_NAVI,
            'from_cache': from_cache,
            'account': account
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts/{account}/projects/{project}/", responses=response_codes, tags=["Account"])
def account_project(account: str, project: str, request: Request):
    raise HTTPException(status_code=501, detail=f"Not implemented. Account: {account}, Project: {project}")


@app.get("/project/{project}/services", response_model=models.ServiceLightList, responses=response_codes,
         tags=["Project"])
def project_service_list(project):
    """List of services of this project"""
    return models.ServiceLightList()


@app.get("/services", responses=response_codes, tags=["Service"])
def services(request: Request, project=None):
    token = _get_token(request)
    if project:
        response = _services.get_services(token=token, projects=[project, ])
    else:
        response = _services.get_services(token=token)
    return {
        'navi': MAIN_NAVI,
        'summary': { 'service_count' : len(response)},
        'services': response
    }

@app.get("/services/{service_name}", response_model=models.Service, responses=response_codes, tags=["Service"])
def service(service_name):
    """
    Detailed service resource. Any endpoint returning potentially large list of items need to requested separately
    and can be paginated.
    """
    return models.Service()


@app.get("/service/{service_name}/backups", response_model=models.BackupList, responses=response_codes, tags=["Service"])
def service_backups(service_name: models.ServiceName):
    """
    Available backups for the service
    """
    return models.BackupList()


@app.get("/service/{service_name}/databases", response_model=models.DatabaseList, responses=response_codes, tags=["Service"])
def service_databases(service_name: models.ServiceName):
    """
    Available backups for the service
    """
    return models.DatabaseList()


@app.get("/service/{service_name}/users", response_model=models.ServiceUserList, responses=response_codes, tags=["Service"])
def service_users(service_name: models.ServiceName):
    """
    Users of the service
    """
    return models.ServiceUserList()


@app.get("/service/{service_name}/integrations", response_model=models.ServiceIntegrationsList, responses=response_codes, tags=["Service"])
def service_integrations(service_name: models.ServiceName):
    """
    Users of the service
    """
    return models.ServiceIntegrationsList()


@app.get("/service/{service_name}/kafka", response_model=models.Kafka, responses=response_codes, tags=["Kafka"])
def kafka_service(service_name: models.ServiceName):
    """
    Kafka specific service data
    """
    return models.Kafka()


@app.get("/service/{service_name}/kafka/topics", response_model=models.KafkaTopics, responses=response_codes, tags=["Kafka"])
def kafka_topics(service_name: models.ServiceName):
    return models.KafkaTopics()


def _find_plan(_service_plans, plan):
    plans = [p for p in _service_plans if p.get('service_plan') == plan]
    assert len(plans) == 1
    p = plans.pop()
    return p


def pagelink(url, paginate_by, page_num):
    return f"{url}&paginate_by={paginate_by}&page={page_num}"


def main():
    uvicorn.run(app)


if __name__ == "__main__":
    main()