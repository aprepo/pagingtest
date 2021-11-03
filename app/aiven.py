import requests
import requests_cache
from requests_cache import CachedSession
import hashlib
import logging

logger = logging.getLogger("aiven-connector")


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
    key = hashlib.sha256(token.encode('utf-8')).hexdigest()
    if key in private_sessions:
        return private_sessions[key]
    else:
        logger.info(f"Creating cached session for hash {key}")
        private_sessions[key] = CachedSession(key, backend="memory", expire_after=60)
        return private_sessions[key]

def get_projects(token):
    session = _get_private_session(token)
    headers = {
        'authorization': token
    }
    response = session.get('https://api.aiven.io/v1/project', headers=headers)
    if response:
        return response.json(), response.from_cache
    else:
        raise Exception(response.json())
