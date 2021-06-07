from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, AnyUrl, Field


class AivenBaseModel(BaseModel):
    #response_created_at: datetime = Field(
    #    description="UTC Timestamp when this REST response was created on the server"
    #)
    pass


class PaginatedAivenBaseModel(AivenBaseModel):
    page: int = Field(description="Current page number")
    prev: int = Field(description="Previous page")
    next: int = Field(description="Next page")
    count: int = Field(description="Total count of items")
    page_count: int = Field(description="Total count of pages available")


class Link(BaseModel):
    href: AnyUrl
    title: Optional[str] = None


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


class ServiceState(Enum):
    RUNNING = "RUNNING"
    REBUILDING = "REBUILDING"
    REBALANCING = "REBALANCING"
    POWEROFF = "POWEROFF"


class Clouds(Enum):
    google = "google"
    aws = "aws"


class Cloud(BaseModel):
    name: Clouds
    description: str


class Network(BaseModel):
    vpc_id: str


class NodesUrl(AnyUrl):
    pass


class Plan(BaseModel):
    name: str
    node_count: int
    node_cpu_count: int
    node_memory_mb : int
    nodes: NodesUrl


class Credentials(BaseModel):
    username: str
    password: str


class ConnectionType(Enum):
    primary = "primary"
    replica = "replica"


class Connection(BaseModel):
    service_uri: AnyUrl
    service_uri_params: str
    connection_type: ConnectionType


class Connections(BaseModel):
    credentials: Credentials
    primary_connection: Connection
    replicas: List[Connection] = []


class Update(BaseModel):
    description: str
    deadline: datetime
    start_after: datetime
    automatic_start_at: datetime


class Maintenance(BaseModel):
    dow: str
    time: datetime
    pending_updates: List[Update] = []


class ServiceMetadata(BaseModel):
    pass


class Notification(BaseModel):
    pass


class ServiceName(str):
    pass


class ServiceLinks(BaseModel):
    self: Link
    integrations: Link
    databases: Link
    backups: Link
    users: Link
    service_details: Optional[Link] = Field(
        description="Service type specific endpoint with more details and actions."
    )


class ServiceLightListItem(BaseModel):
    service_name: ServiceName
    service_type: ServiceType
    service_type_description: str
    service_state: ServiceState
    service_details: AnyUrl
    links : ServiceLinks = Field(alias="_links")


class ServiceLightList(PaginatedAivenBaseModel):
    total_service_count: int
    services: List[ServiceLightListItem] = []


class Service(AivenBaseModel):
    service_name: ServiceName = Field(description="Name of the service, may or may not be same as in URL")
    service_type: ServiceType = Field(description="Service type")
    service_type_description: str
    service_state: ServiceState = Field(description="Overall state of the service")
    connections: Connections = Field(description="Connection strings and credentials")
    cloud: Cloud
    plan: Plan
    network: Network
    maintenance: Maintenance
    metadata: ServiceMetadata
    notifications: List[Notification] = []
    features: List[str] = []
    created_at: datetime = Field(description="Service (instance) creation time, UTC time")
    links : ServiceLinks = Field(alias="_links")


class Backup(BaseModel):
    backup_name: str
    backup_time: datetime
    data_size: int


class BackupList(PaginatedAivenBaseModel):
    backups: List[Backup] =[]


class ProjectListItem(BaseModel):
    project_name: str
    href: AnyUrl


class ProjectList(AivenBaseModel):
    projects: List[ProjectListItem] = []


class Project(AivenBaseModel):
    name: str
    services: ServiceLightList


class DatabaseListItem(BaseModel):
    database_name: str


class DatabaseList(PaginatedAivenBaseModel):
    items: List[DatabaseListItem] = []


class ServiceUserListItem(BaseModel):
    pass


class ServiceUserList(PaginatedAivenBaseModel):
    items: List[ServiceUserListItem] = []


class IntegrationType(Enum):
    replication = "replication"
    logs = "logs"
    metrics = "metrics"


class Endpoint(BaseModel):
    name: str
    href: AnyUrl


class ServiceIntegrationsListItem(BaseModel):
    integration_type = IntegrationType
    target_endpoint = Endpoint
    source_endpoint = Endpoint


class ServiceIntegrationsList(PaginatedAivenBaseModel):
    items: List[ServiceIntegrationsListItem] = []


class KafkaTopicLinks(BaseModel):
    messages: Link


class KafkaTopic(BaseModel):
    name: str
    links: KafkaTopicLinks


class KafkaTopics(PaginatedAivenBaseModel):
    topics: List[KafkaTopic]


class KafkaServiceLinks(BaseModel):
    self: Link
    parent: Link
    acl: Link
    connectors: Link
    topics: Link


class Kafka(AivenBaseModel):
    links: KafkaServiceLinks = Field(alias="_links")