from collections import OrderedDict
from itertools import islice

from fastapi import FastAPI
import uvicorn
import aiven
from loguru import logger

app = FastAPI()

@app.get("/")
def index():
    return {
        "docs": app.docs_url,
        "service_types": app.servers
    }


@app.get("/service_types")
def service_types():
    return aiven.get_service_types()


@app.get("/service_types/{service_type}")
def service_type(service_type):
    serfice_types = aiven.get_service_types().get('service_types', {})
    return serfice_types.get(service_type)


@app.get("/service_types/{service_type}/service_plans")
def service_plans(service_type):
    serfice_types = aiven.get_service_types().get('service_types', {})
    plans = {
        'service': {
            'type': service_type,
            'url': f"http://localhost:8000/service_types/{service_type}"
        },
        'plans': [
            {
                'plan': plan.get('service_plan'),
                'url': f"http://localhost:8000/service_types/{service_type}/service_plans/{plan.get('service_plan')}"
            }
            for plan in serfice_types.get(service_type).get('service_plans') if plan.get('service_plan') != plan
        ]
    }
    return plans


@app.get("/service_types/{service_type}/service_plans/{plan}")
def service_plan(service_type, plan):
    serfice_types = aiven.get_service_types().get('service_types', {})
    plans = [p for p in serfice_types.get(service_type).get('service_plans') if p.get('service_plan') == plan]
    assert len(plans) == 1
    return {
        "all_plans": {
            "url": f"http://localhost:8000/service_types/{service_type}/service_plans"
        },
        "plan": plans.pop()
    }


@app.get("/service_types/{service_type}/service_plans/{plan}/regions")
def service_plan_regions(service_type, plan, order_by="name", filter: str = None, page: int = None, paginate_by: int = None):
    if paginate_by:
        if page is None or int(page) < 1:
            page = 1

    url = f"http://localhost:8000/service_types/{service_type}/service_plans/{plan}/regions?"

    FIELDS = {"id", "disk_space_mb", "price_usd", "node_memory_mb"}
    service_types = aiven.get_service_types().get('service_types', {})
    plans = [p for p in service_types.get(service_type).get('service_plans') if p.get('service_plan') == plan]
    assert len(plans) == 1
    p = plans.pop()

    regions: dict = p.get("regions", dict())
    num_regions = len(regions)
    region_keys = [k for k in regions.keys()]
    ordered_list = OrderedDict()
    region_keys.sort()

    # 1: Order
    for k in region_keys:
        ordered_list[k] = regions.get(k)

    # 2: Paginate
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
                "all_plans": f"http://localhost:8000/service_types/{service_type}/service_plans",
                "this_plan": f"http://localhost:8000/service_types/{service_type}/service_plans",
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


def pagelink(url, paginate_by, page_num):
    return f"{url}&paginate_by={paginate_by}&page={page_num}"


def main():
    uvicorn.run(app)


if __name__ == "__main__":
    main()