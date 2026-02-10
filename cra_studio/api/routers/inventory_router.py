from fastapi import APIRouter

from cra_studio.api.schemas import ProductIn
from cra_studio.repositories.inventory_repo import create_product, list_products

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/products")
def add_product(payload: ProductIn):
    create_product(payload.organization_id, payload.name, payload.product_type, payload.family, payload.market)
    return {"status": "ok"}


@router.get("/products")
def get_products():
    return list_products().to_dict(orient="records")
