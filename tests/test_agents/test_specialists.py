from src.agents.specialists import get_specialist
from src.agents.specialists.data import analyze as analyze_data
from src.agents.specialists.infra import analyze as analyze_infra
from src.agents.specialists.ml import analyze as analyze_ml
from src.agents.specialists.platform import analyze as analyze_platform
from src.agents.specialists.product import analyze as analyze_product
from src.infrastructure.models import Department


class TestGetSpecialist:
    def test_given_platform_when_get_specialist_then_returns_platform_analyze(self):
        assert get_specialist(Department.PLATFORM) == analyze_platform

    def test_given_data_when_get_specialist_then_returns_data_analyze(self):
        assert get_specialist(Department.DATA) == analyze_data

    def test_given_product_when_get_specialist_then_returns_product_analyze(self):
        assert get_specialist(Department.PRODUCT) == analyze_product

    def test_given_ml_when_get_specialist_then_returns_ml_analyze(self):
        assert get_specialist(Department.ML) == analyze_ml

    def test_given_infra_when_get_specialist_then_returns_infra_analyze(self):
        assert get_specialist(Department.INFRA) == analyze_infra
