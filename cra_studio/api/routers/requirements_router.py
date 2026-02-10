from fastapi import APIRouter

from cra_studio.api.schemas import RequirementIn
from cra_studio.repositories.requirements_repo import create_requirement, deactivate_requirement, list_requirements

router = APIRouter(prefix="/requirements", tags=["requirements"])


@router.post("")
def add_requirement(payload: RequirementIn):
    create_requirement(
        (
            payload.req_id,
            payload.title,
            payload.text,
            payload.source,
            payload.tags,
            payload.evidence_examples,
            payload.test_method,
            payload.severity,
            payload.weight,
            payload.version,
            payload.effective_date,
            payload.supersedes,
        )
    )
    return {"status": "ok"}


@router.patch("/{req_id}/deactivate")
def deactivate(req_id: str):
    deactivate_requirement(req_id)
    return {"status": "ok"}


@router.get("")
def get_requirements(active_only: bool = True):
    return list_requirements(active_only=active_only).to_dict(orient="records")
