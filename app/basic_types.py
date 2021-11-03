from enum import Enum
from typing import Any
from pydantic import BaseModel, AnyUrl


class ServiceType(Enum):
    kafka = "kafka"
    m3db = "m3db"
    m3aggregator = "m3aggregator"
    mysql = "mysql"
    pg = "pg"
    redis = "redis"
    cassandra = "cassandra"
    grafana = "grafana"
    influxdb = "influxdb"
    elasticsearch = "elasticsearch"
    opensearch = "opensearch"
    kafka_connect = "kafka_connect"
    kafka_mirrormaker = "kafka_mirrormaker"


class AivenNavi(BaseModel):
    docs: AnyUrl
    redoc: AnyUrl
    home: AnyUrl
    service_types: AnyUrl
    accounts: AnyUrl
    projects: AnyUrl
    services: AnyUrl


class ServiceTypeListItem(BaseModel):
    name: ServiceType
    url: AnyUrl

