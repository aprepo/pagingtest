from enum import Enum
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
    kafka_connect = "kafka_connect"
    kafka_mirrormaker = "kafka_mirrormaker"


class AivenNavi(BaseModel):
    docs: AnyUrl
    redoc: AnyUrl
    home: AnyUrl


class ServiceTypeListItem(BaseModel):
    name: ServiceType
    url: AnyUrl

