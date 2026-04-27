from src.agents.specialists.data import analyze as analyze_data
from src.agents.specialists.infra import analyze as analyze_infra
from src.agents.specialists.ml import analyze as analyze_ml
from src.agents.specialists.platform import analyze as analyze_platform
from src.agents.specialists.product import analyze as analyze_product
from src.infrastructure.models import Department

SPECIALISTS = {
    Department.PLATFORM: analyze_platform,
    Department.DATA: analyze_data,
    Department.PRODUCT: analyze_product,
    Department.ML: analyze_ml,
    Department.INFRA: analyze_infra,
}


def get_specialist(department: Department):
    return SPECIALISTS.get(department, analyze_infra)
