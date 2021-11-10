import requests_cache
from requests_cache import CachedSession
import hashlib
from logging import getLogger


logger = getLogger("cache")


session = CachedSession('shared_cache', backend='memory')
private_sessions = {}    # Way too simple session cache


def get_shared_session():
    return session


def get_private_session(token):
    print(f"TOKEN : [{token[:15]}***********]")
    key = hashlib.sha256(token.encode('utf-8')).hexdigest()
    if key in private_sessions:
        return private_sessions[key]
    else:
        logger.warn(f"Creating cached session for hash {key}")
        private_sessions[key] = CachedSession(key, backend="memory", expire_after=60)
        return private_sessions[key]


def get_cache_session_count():
    return len(private_sessions)

def get_cache_response_count():
    counter = 0
    for key in private_sessions.keys():
        session = private_sessions[key]
        counter = counter + session.cache.response_count()
    return counter

