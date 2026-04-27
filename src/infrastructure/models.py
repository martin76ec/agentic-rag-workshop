from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class Department(StrEnum):
    PLATFORM = "platform"
    DATA = "data"
    PRODUCT = "product"
    ML = "ml"
    INFRA = "infra"


class Service(BaseModel):
    name: str
    department: Department
    description: str
    tier: int = Field(ge=1, le=3, description="1=critical, 2=important, 3=auxiliary")
    region: str = "us-east-1"
    depends_on: list[str] = Field(default_factory=list, description="Names of services this depends on")
    sla_minutes: float = Field(description="Target downtime SLA in minutes per month")
    tags: list[str] = Field(default_factory=list)
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata")

    model_config = {"populate_by_name": True}


class Dependency(BaseModel):
    source: str
    target: str
    relation: str = "depends_on"
    critical: bool = True


class Incident(BaseModel):
    incident_id: str
    service_name: str
    severity: Severity
    description: str
    symptoms: list[str] = Field(default_factory=list)
    timestamp: str = ""
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata")

    model_config = {"populate_by_name": True}


class BlastRadiusReport(BaseModel):
    incident_id: str
    root_service: str
    affected_services: list[str]
    affected_departments: list[Department]
    propagation_paths: list[list[str]]
    estimated_impact: Severity
    recommended_actions: list[str] = Field(default_factory=list)


class HealthCheckResult(BaseModel):
    service_name: str
    status: HealthStatus
    latency_ms: float = 0.0
    error_rate: float = 0.0
    message: str = ""
    timestamp: str = ""


class MetricPoint(BaseModel):
    service_name: str
    metric: str
    value: float
    unit: str = ""
    timestamp: str = ""
