from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, AnyUrl, Field
from app import basic_types


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


class ServiceBillingState(Enum):
    active_trial = "active_trial"
    no_billing_method = "no_billing_method"
    invalid = "invalid"
    valid = "valid"


class AivenNavi(BaseModel):
    docs: AnyUrl = Field(description="Swagger docs")
    redoc: AnyUrl = Field(description="OpenAPI docs")
    home: AnyUrl = Field(description="API root")
    service_types: AnyUrl = Field(description="Publicly available service types")
    accounts: AnyUrl = Field(description="All available accounts")
    projects: AnyUrl = Field(description="All available projects, from all accounts and without accounts")
    services: AnyUrl = Field(description="All available services, from all accounts and projects.")


class ServiceTypeListItem(BaseModel):
    name: ServiceType
    url: AnyUrl


class AccountShortItem(BaseModel):
    account_id: str
    account_name: str
    url: AnyUrl



class BillingShortItem(BaseModel):
    billing_group_id: str
    billing_group_name: str
    state: basic_types.ServiceBillingState = Field(description="True if the billing method is valid and services are allowd to run on this service")
    url: Optional[AnyUrl] = None


class ProjectListItem(BaseModel):
    tenant_id: str = Field(description="Aiven platform supports multiple tenants. The usual value here is 'aiven'.")
    project_name: str
    account: Optional[AccountShortItem] = Field(None, description="Project may or may not be a part of an Account")
    billing: BillingShortItem = Field(description="References to billing information.")
    services: AnyUrl