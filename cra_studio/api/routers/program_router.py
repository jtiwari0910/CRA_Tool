from fastapi import APIRouter

from cra_studio.api.schemas import OrganizationIn
from cra_studio.repositories.program_repo import create_organization, list_organizations

router = APIRouter(prefix="/program", tags=["program"])


@router.post("/organizations")
def add_organization(payload: OrganizationIn):
    create_organization(payload.name, payload.org_type, payload.markets)
    return {"status": "ok"}


@router.get("/organizations")
def get_organizations():
    return list_organizations().to_dict(orient="records")
