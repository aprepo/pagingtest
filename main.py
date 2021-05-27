from collections import OrderedDict
from itertools import islice

from fastapi import FastAPI
import uvicorn
import aiven
from loguru import logger
from os import environ as env

app = FastAPI()

HOST = env.get("HOST", "localhost")
PORT = env.get("PORT", "8000")
BASEURL = env.get("BASEURL", f"http://{HOST}:{PORT}")

MAIN_NAVI = {
    'docs': f"{BASEURL}{app.docs_url}",
    'home': f"{BASEURL}/",
    "service_types": f"{BASEURL}/service_types",
}


@app.get("/")
def index():
    return {
        "nav": MAIN_NAVI,
    }


@app.get("/service_types")
def service_types():
    service_types = aiven.get_service_types()
    return {
        "nav": MAIN_NAVI,
        'service_types': [
            {'name': key, 'url': f"{BASEURL}/service_types/{key}"} for key in service_types["service_types"].keys()
        ]
    }


@app.get("/service_types/{service_type}")
def service_type(service_type):
    service_types = aiven.get_service_types().get('service_types', {})
    properties = service_types.get(service_type)
    _plans_base_url = f"{BASEURL}/service_types/{service_type}/service_plans/"

    def versions(props):
        #schema = props.get("user_config_schema", {})
        #props2 = schema.get("properties", {})
        #kafka_version = props2.get("kafka_version", {})
        #kafka_versions = kafka_version.get("enum", [])
        #return kafka_versions
        return aiven.get_service_versions(service_type)

    return {
        "nav": MAIN_NAVI,
        "service_type": {
            "name": service_type,
            "description": properties.get("description"),
            "versions" : {
                "latest_available_version": properties.get("latest_available_version"),
                "default_version": properties.get("default_version"),
                #"all_versions": versions(properties),
                "all_versions": f"{BASEURL}/service_types/{service_type}/versions"
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
            #"properties" : properties,
        },
    }

@app.get("/service_types/{service_type}/versions")
def service_versions(service_type):
    return {
        "nav": MAIN_NAVI,
        "service_type": {
            "name": service_type,
            "url": f"{BASEURL}/service_types/{service_type}/"
        },
        "versions": aiven.get_service_versions(service_type)
    }

@app.get("/service_types/{service_type}/service_plans")
def service_plans(service_type):
    service_types = aiven.get_service_types().get('service_types', {})
    plans = {
        "nav": MAIN_NAVI,
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


@app.get("/service_types/{service_type}/service_plans/{plan}")
def service_plan(service_type, plan):
    serfice_types = aiven.get_service_types().get('service_types', {})
    plans = [p for p in serfice_types.get(service_type).get('service_plans') if p.get('service_plan') == plan]
    assert len(plans) == 1
    return {
        "nav": MAIN_NAVI,
        'service_type': {
            'name': service_type,
            'url': f"{BASEURL}/service_types/{service_type}"
        },
        "all_plans": {
            "url": f"{BASEURL}/service_types/{service_type}/service_plans"
        },
        "plan": plans.pop()
    }


@app.get("/service_types/{service_type}/service_plans/{plan}/regions")
def service_plan_regions(service_type, plan, order_by="name", filter: str = None, page: int = None, paginate_by: int = None):
    if paginate_by:
        if page is None or int(page) < 1:
            page = 1

    url = f"{BASEURL}/service_types/{service_type}/service_plans/{plan}/regions?"

    FIELDS = {"id", "disk_space_mb", "price_usd", "node_memory_mb"}
    _service_plans = aiven.get_service_types().get('service_types', {}).get(service_type).get('service_plans', {})
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