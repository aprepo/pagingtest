from app.aiven import cache
from app.aiven import headers
from app.aiven import projects as aiven_projects
from app.settings import BASEURL


def get_service_types():
    response = cache.get_shared_session().get("https://api.aiven.io/v1/service_types")
    return response.json(), response.from_cache


def get_service_versions(service_name=None):
    response = cache.get_shared_session().get("https://api.aiven.io/v1/service_versions")
    versions = response.json().get("service_versions")
    if service_name:
        versions = {
            version.get("major_version") :
            {
                "state": version.get("state"),
                "lifecycle": {
                    "upstream_end_of_life_time": version.get("upstream_end_of_life_time"),
                    "aiven_end_of_life_time": version.get("aiven_end_of_life_time"),
                    "aiven_availability_end_time": version.get("availability_end_time"),
                    "aiven_availability_start_time": version.get("availability_start_time"),
                    "aiven_end_of_life_help_article_url": version.get("end_of_life_help_article_url"),
                    "aiven_termination_time": version.get("termination_time"),
                }
            }
            for version in versions if version.get("service_type") == service_name
        }
    return versions


def get_services_for_project(token, project):
    session = cache.get_private_session(token)
    response = session.get(f"https://api.aiven.io/v1/project/{project}/service", headers=headers.get_headers(token))
    services = [s.get('service_name') for s in response.json().get('services')]
    return services, response.from_cache


def get_services(token, projects=[]):
    """
    Get services from projects. If no project is defined, returns _all_ services from all projects the user has access to.
    """
    return_value = []

    if projects:
        pass
    else:
        json_data, from_cache = aiven_projects.get_projects(token)
        projects = [p.get('project_name') for p in json_data.get('projects')]

    for project in projects:
        print(f"Project: {project}")
        services, _ = get_services_for_project(token, project)
        for service in services:
            return_value.append(
                {
                    "account": {
                        "name": "NOT IMPLEMENTED",
                        "url": "NOT IMPLEMENTED"
                    },
                    "project": { 
                        "name": project, 
                        "url": f"{BASEURL}/projects/{project}/"
                        },
                    "service": { 
                        "name": service, 
                        "url": f"{BASEURL}/projects/{project}/services/{service}/"
                        }
                }
            )
    return return_value