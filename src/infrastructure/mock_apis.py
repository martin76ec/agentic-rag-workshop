import random
import uuid
from datetime import UTC, datetime

from src.infrastructure.models import (
    HealthCheckResult,
    HealthStatus,
    Incident,
    MetricPoint,
    Severity,
)
from src.infrastructure.topology import SERVICES, get_service_by_name

INCIDENT_TEMPLATES: list[dict] = [
    {
        "description": "High latency detected on {service}",
        "severity": Severity.HIGH,
        "symptoms": ["latency_spike", "slow_responses", "timeout_errors"],
    },
    {
        "description": "Service {service} is returning 5xx errors",
        "severity": Severity.CRITICAL,
        "symptoms": ["5xx_errors", "error_rate_above_threshold", "alert_fired"],
    },
    {
        "description": "Memory usage above 90% on {service}",
        "severity": Severity.HIGH,
        "symptoms": ["memory_pressure", "oom_risk", "performance_degradation"],
    },
    {
        "description": "Connection pool exhaustion on {service}",
        "severity": Severity.MEDIUM,
        "symptoms": ["connection_timeout", "pool_exhausted", "queue_backlog"],
    },
    {
        "description": "Disk usage warning on {service}",
        "severity": Severity.LOW,
        "symptoms": ["disk_usage_80pct", "slow_writes", "io_wait_high"],
    },
    {
        "description": "Replication lag detected on {service}",
        "severity": Severity.MEDIUM,
        "symptoms": ["replication_lag", "stale_reads", "data_inconsistency"],
    },
    {
        "description": "Certificate expiring in 7 days on {service}",
        "severity": Severity.LOW,
        "symptoms": ["cert_expiry_warning", "mTLS_degradation"],
    },
    {
        "description": "Pod crashes and restart loop on {service}",
        "severity": Severity.CRITICAL,
        "symptoms": ["crash_loop", "pod_restart", "health_check_failure"],
    },
]


def generate_health_check(service_name: str, force_status: HealthStatus | None = None) -> HealthCheckResult:
    service = get_service_by_name(service_name)
    if not service:
        return HealthCheckResult(
            service_name=service_name,
            status=HealthStatus.UNKNOWN,
            message=f"Service {service_name} not found in topology",
        )

    if force_status:
        status = force_status
    else:
        roll = random.random()
        if roll < 0.75:
            status = HealthStatus.HEALTHY
        elif roll < 0.92:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.DOWN

    now = datetime.now(UTC).isoformat()

    if status == HealthStatus.HEALTHY:
        return HealthCheckResult(
            service_name=service_name,
            status=status,
            latency_ms=random.uniform(1.0, 50.0),
            error_rate=random.uniform(0.0, 0.01),
            message="OK",
            timestamp=now,
        )
    elif status == HealthStatus.DEGRADED:
        return HealthCheckResult(
            service_name=service_name,
            status=status,
            latency_ms=random.uniform(200.0, 2000.0),
            error_rate=random.uniform(0.05, 0.15),
            message="Degraded performance detected",
            timestamp=now,
        )
    else:
        return HealthCheckResult(
            service_name=service_name,
            status=status,
            latency_ms=random.uniform(5000.0, 30000.0),
            error_rate=random.uniform(0.5, 1.0),
            message="Service unavailable",
            timestamp=now,
        )


def generate_all_health_checks(force_down: list[str] | None = None) -> list[HealthCheckResult]:
    force_down = force_down or []
    results = []
    for service in SERVICES:
        status = HealthStatus.DOWN if service.name in force_down else None
        results.append(generate_health_check(service.name, force_status=status))
    return results


def generate_incident(service_name: str, template_index: int | None = None) -> Incident:
    service = get_service_by_name(service_name)
    if not service:
        raise ValueError(f"Service {service_name} not found in topology")

    template = (
        INCIDENT_TEMPLATES[template_index]
        if template_index is not None
        else random.choice(INCIDENT_TEMPLATES)
    )

    return Incident(
        incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
        service_name=service_name,
        severity=template["severity"],
        description=template["description"].format(service=service_name),
        symptoms=template["symptoms"],
        timestamp=datetime.now(UTC).isoformat(),
        metadata={"department": service.department.value, "tier": service.tier},
    )


def generate_random_incident() -> Incident:
    service = random.choice(SERVICES)
    return generate_incident(service.name)


def generate_metrics(service_name: str, count: int = 10) -> list[MetricPoint]:
    now = datetime.now(UTC)
    points = []
    metrics_config = [
        ("cpu_percent", 0, 100, "%"),
        ("memory_percent", 0, 100, "%"),
        ("request_rate", 0, 5000, "req/s"),
        ("error_rate", 0, 1, "%"),
        ("latency_p50", 1, 500, "ms"),
        ("latency_p99", 10, 5000, "ms"),
    ]

    for metric_name, min_val, max_val, unit in metrics_config:
        for i in range(count):
            value = random.uniform(min_val, max_val)
            ts = now.replace(microsecond=0).isoformat()
            points.append(
                MetricPoint(
                    service_name=service_name,
                    metric=metric_name,
                    value=round(value, 2),
                    unit=unit,
                    timestamp=ts,
                )
            )

    return points
