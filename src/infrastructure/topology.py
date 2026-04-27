from src.infrastructure.models import Department, Dependency, Service

SERVICES: list[Service] = [
    Service(
        name="api-gateway",
        department=Department.PLATFORM,
        description="Main API gateway handling all external traffic routing and rate limiting",
        tier=1,
        region="us-east-1",
        depends_on=[],
        sla_minutes=4.38,
        tags=["ingress", "routing", "rate-limiting"],
        metadata={"port": 8080, "protocol": "https", "owners": ["platform-team"]},
    ),
    Service(
        name="auth-service",
        department=Department.PLATFORM,
        description="OAuth2/OIDC authentication and authorization service",
        tier=1,
        region="us-east-1",
        depends_on=["api-gateway"],
        sla_minutes=4.38,
        tags=["auth", "oidc", "jwt"],
        metadata={"port": 8443, "protocol": "gRPC", "owners": ["platform-team"]},
    ),
    Service(
        name="config-service",
        department=Department.PLATFORM,
        description="Centralized configuration management and feature flag service",
        tier=2,
        region="us-east-1",
        depends_on=["api-gateway"],
        sla_minutes=26.28,
        tags=["config", "feature-flags"],
        metadata={"port": 8090, "protocol": "http", "owners": ["platform-team"]},
    ),
    Service(
        name="service-mesh",
        department=Department.PLATFORM,
        description="Istio-based service mesh for inter-service communication and observability",
        tier=1,
        region="us-east-1",
        depends_on=["api-gateway"],
        sla_minutes=4.38,
        tags=["mesh", "proxy", "mTLS"],
        metadata={"port": 15001, "protocol": "gRPC", "owners": ["platform-team"]},
    ),
    Service(
        name="postgres-primary",
        department=Department.DATA,
        description="Primary PostgreSQL database for transactional data",
        tier=1,
        region="us-east-1",
        depends_on=["service-mesh"],
        sla_minutes=4.38,
        tags=["database", "postgresql", "primary"],
        metadata={"port": 5432, "protocol": "tcp", "owners": ["data-team"]},
    ),
    Service(
        name="redis-cache",
        department=Department.DATA,
        description="Redis cluster for caching and session storage",
        tier=1,
        region="us-east-1",
        depends_on=["service-mesh"],
        sla_minutes=4.38,
        tags=["cache", "redis", "sessions"],
        metadata={"port": 6379, "protocol": "tcp", "owners": ["data-team"]},
    ),
    Service(
        name="kafka-broker",
        department=Department.DATA,
        description="Apache Kafka cluster for event streaming and async messaging",
        tier=1,
        region="us-east-1",
        depends_on=["service-mesh"],
        sla_minutes=4.38,
        tags=["messaging", "kafka", "events"],
        metadata={"port": 9092, "protocol": "tcp", "owners": ["data-team"]},
    ),
    Service(
        name="clickhouse-analytics",
        department=Department.DATA,
        description="ClickHouse columnar database for analytics and time-series queries",
        tier=2,
        region="us-east-1",
        depends_on=["service-mesh", "kafka-broker"],
        sla_minutes=26.28,
        tags=["analytics", "clickhouse", "olap"],
        metadata={"port": 8123, "protocol": "http", "owners": ["data-team"]},
    ),
    Service(
        name="order-service",
        department=Department.PRODUCT,
        description="Core order management and lifecycle service",
        tier=1,
        region="us-east-1",
        depends_on=["api-gateway", "postgres-primary", "kafka-broker"],
        sla_minutes=4.38,
        tags=["orders", "transactions"],
        metadata={"port": 8081, "protocol": "http", "owners": ["product-team"]},
    ),
    Service(
        name="inventory-service",
        department=Department.PRODUCT,
        description="Real-time inventory tracking and availability management",
        tier=1,
        region="us-east-1",
        depends_on=["api-gateway", "postgres-primary", "redis-cache"],
        sla_minutes=4.38,
        tags=["inventory", "stock"],
        metadata={"port": 8082, "protocol": "http", "owners": ["product-team"]},
    ),
    Service(
        name="payment-service",
        department=Department.PRODUCT,
        description="Payment processing and integration with payment providers",
        tier=1,
        region="us-east-1",
        depends_on=["api-gateway", "postgres-primary", "kafka-broker"],
        sla_minutes=4.38,
        tags=["payments", "stripe", "billing"],
        metadata={"port": 8083, "protocol": "http", "owners": ["product-team"]},
    ),
    Service(
        name="notification-service",
        department=Department.PRODUCT,
        description="Multi-channel notification delivery (email, SMS, push)",
        tier=2,
        region="us-east-1",
        depends_on=["api-gateway", "kafka-broker"],
        sla_minutes=26.28,
        tags=["notifications", "email", "sms"],
        metadata={"port": 8084, "protocol": "http", "owners": ["product-team"]},
    ),
    Service(
        name="feature-store",
        department=Department.ML,
        description="Centralized feature store for ML model training and serving features",
        tier=2,
        region="us-east-1",
        depends_on=["redis-cache", "postgres-primary"],
        sla_minutes=26.28,
        tags=["ml", "features", "offline"],
        metadata={"port": 9090, "protocol": "http", "owners": ["ml-team"]},
    ),
    Service(
        name="model-serving",
        department=Department.ML,
        description="Real-time ML model inference service with A/B testing",
        tier=2,
        region="us-east-1",
        depends_on=["feature-store", "api-gateway"],
        sla_minutes=26.28,
        tags=["ml", "inference", "serving"],
        metadata={"port": 9091, "protocol": "http", "owners": ["ml-team"]},
    ),
    Service(
        name="training-pipeline",
        department=Department.ML,
        description="Batch ML training pipeline orchestration (Kubeflow)",
        tier=3,
        region="us-east-1",
        depends_on=["feature-store", "kafka-broker"],
        sla_minutes=43.8,
        tags=["ml", "training", "kubeflow"],
        metadata={"port": 9092, "protocol": "http", "owners": ["ml-team"]},
    ),
    Service(
        name="experiment-tracker",
        department=Department.ML,
        description="ML experiment tracking and model registry (MLflow)",
        tier=3,
        region="us-east-1",
        depends_on=["postgres-primary", "clickhouse-analytics"],
        sla_minutes=43.8,
        tags=["ml", "experiments", "mlflow"],
        metadata={"port": 9093, "protocol": "http", "owners": ["ml-team"]},
    ),
    Service(
        name="k8s-controller",
        department=Department.INFRA,
        description="Kubernetes control plane and cluster management",
        tier=1,
        region="us-east-1",
        depends_on=["service-mesh"],
        sla_minutes=4.38,
        tags=["k8s", "control-plane", "scheduling"],
        metadata={"port": 6443, "protocol": "https", "owners": ["infra-team"]},
    ),
    Service(
        name="monitoring-agent",
        department=Department.INFRA,
        description="Prometheus + Grafana monitoring stack and alerting",
        tier=1,
        region="us-east-1",
        depends_on=["service-mesh", "k8s-controller"],
        sla_minutes=4.38,
        tags=["monitoring", "prometheus", "grafana"],
        metadata={"port": 9090, "protocol": "http", "owners": ["infra-team"]},
    ),
    Service(
        name="ci-runner",
        department=Department.INFRA,
        description="CI/CD pipeline runner (GitHub Actions, ArgoCD)",
        tier=2,
        region="us-east-1",
        depends_on=["k8s-controller"],
        sla_minutes=26.28,
        tags=["ci", "cd", "deployments"],
        metadata={"port": 8080, "protocol": "http", "owners": ["infra-team"]},
    ),
    Service(
        name="dns-resolver",
        department=Department.INFRA,
        description="Internal DNS resolution and service discovery",
        tier=1,
        region="us-east-1",
        depends_on=["service-mesh", "k8s-controller"],
        sla_minutes=4.38,
        tags=["dns", "discovery", "coredns"],
        metadata={"port": 53, "protocol": "udp", "owners": ["infra-team"]},
    ),
]

DEPENDENCIES: list[Dependency] = [
    Dependency(source=s.name, target=d, critical=s.tier <= 2)
    for s in SERVICES
    for d in s.depends_on
]


def get_service_by_name(name: str) -> Service | None:
    return next((s for s in SERVICES if s.name == name), None)


def get_services_by_department(department: Department) -> list[Service]:
    return [s for s in SERVICES if s.department == department]


def get_dependents(service_name: str) -> list[Service]:
    return [s for s in SERVICES if service_name in s.depends_on]


def get_dependencies(service_name: str) -> list[Service]:
    service = get_service_by_name(service_name)
    if not service:
        return []
    return [s for s in SERVICES if s.name in service.depends_on]
