import requests


def get_service_types():
    response = requests.get("https://api.aiven.io/v1/service_types")
    return response.json()