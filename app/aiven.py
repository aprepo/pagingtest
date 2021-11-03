import requests
import requests_cache
from requests_cache import CachedSession
import hashlib
import logging
from os import environ as env

from requests_cache.models import response

logger = logging.getLogger("aiven-connector")

# TODO meve these to some better place
HOST = env.get("HOST", "localhost")
PORT = env.get("PORT", "8000")
BASEURL = env.get("BASEURL", f"http://{HOST}:{PORT}")


session = CachedSession('shared_cache', backend='memory')
private_sessions = {}    # Way too simple session cache

def get_service_types():
    response = session.get("https://api.aiven.io/v1/service_types")
    return response.json(), response.from_cache


def get_service_versions(service_name=None):
    response = session.get("https://api.aiven.io/v1/service_versions")
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

def _get_private_session(token):
    print(f"TOKEN : [{token[:15]}***********]")
    key = hashlib.sha256(token.encode('utf-8')).hexdigest()
    if key in private_sessions:
        return private_sessions[key]
    else:
        logger.info(f"Creating cached session for hash {key}")
        private_sessions[key] = CachedSession(key, backend="memory", expire_after=60)
        return private_sessions[key]

def _get_headers(token):
    headers = {
        'authorization': token,
        'User-agent': 'paging-test'
    }
    return headers

def get_accounts(token):
    session = _get_private_session(token)
    headers = _get_headers(token)
    response = session.get('https://api.aiven.io/v1/account', headers=headers)
    accounts = []
    for account in response.json().get('accounts', []):
        account['url'] = f"{BASEURL}/accounts/{account.get('account_id', None)}/"
        accounts.append(account)
    return accounts, response.from_cache


def get_account(token, account_id):
    session = _get_private_session(token)
    headers = _get_headers(token)
    response = session.get('https://api.aiven.io/v1/account/{account_id}', headers=headers)
    return response.json(), response.from_cache

def get_projects(token):
    session = _get_private_session(token)
    headers = _get_headers(token)
    response = session.get('https://api.aiven.io/v1/project', headers=headers)
    if response:
        return_value = { 'from_cache': response.from_cache, 'projects': []}

        def _billing_group_url_or_none(account_id, group_id):
            if group_id is None or account_id is None:
                return None
            return f"{BASEURL}/accounts/{account_id}/billing_group/{group_id}"

        def _account_or_none(account_id, account_name):
            if account_id is None or account_name is None:
                return None
            else:
                return {
                    'account_id': account_id,
                    'account_name': account_name,
                    'url': f"{BASEURL}/accounts/{account_id}/",
                }

        for project in response.json().get("projects", []):
            return_value['projects'].append({
                'tenant_id': project.get('tenant_id', None),
                'project_name': project.get('project_name', None),
                'account': _account_or_none(
                    project.get('account_id', None), 
                    project.get('account_name', None)
                    ),
                'billing': {
                    'billing_group_id': project.get('billing_group_id', None),
                    'billing_group_name': project.get('billing_group_name', None),
                    "url": _billing_group_url_or_none(
                        project.get('account_id', None), 
                        project.get('billing_group_id')
                        )
                }
            })
        return return_value, response.from_cache
    else:
        raise Exception(response.json())

def get_services(token, projects=[]):
    """
    Get services from projects. If no project is defined, returns _all_ services from all projects the user has access to.
    """
    session = _get_private_session(token)
    headers = _get_headers(token)

    return_value = []

    if not projects:
        projects = get_projects(token)

    for project_name in projects:
        services = get_services(token, project_name)
        for service in services:
            return_value.append(
                {
                    "account": {
                        "name": "NOT IMPLEMENTED",
                        "url": "NOT IMPLEMENTED"
                    },
                    "project": { 
                        "name": project_name, 
                        "url": f"{BASEURL}/projects/{project_name}/"
                        },
                    "service": { 
                        "name": service, 
                        "url": f"{BASEURL}/projects/{project_name}/services/{service}/"
                        }
                }
            )
    return return_value