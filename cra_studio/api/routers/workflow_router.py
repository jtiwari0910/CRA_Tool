from fastapi import APIRouter

from cra_studio.api.schemas import (
    ActionIn,
    ApplicabilityIn,
    AssessmentIn,
    AuditIn,
    CriticalityIn,
    EconomicRoleIn,
    EvidenceIn,
    VulnerabilityIn,
)
from cra_studio.repositories.workflow_repo import (
    create_action,
    create_applicability,
    create_assessment,
    create_audit,
    create_criticality,
    create_economic_role,
    create_evidence,
    create_vulnerability,
    list_table,
)

router = APIRouter(tags=["workflow"])


@router.post("/applicability/decisions")
def add_applicability(payload: ApplicabilityIn):
    create_applicability(payload.product_id, int(payload.in_scope), payload.justification, payload.decision_date)
    return {"status": "ok"}


@router.get("/applicability/decisions")
def get_applicability():
    return list_table("applicability").to_dict(orient="records")


@router.post("/economic-roles")
def add_economic_role(payload: EconomicRoleIn):
    create_economic_role(payload.product_id, payload.role, payload.owner, payload.traceability_notes)
    return {"status": "ok"}


@router.get("/economic-roles")
def get_economic_roles():
    return list_table("economic_roles").to_dict(orient="records")


@router.post("/criticality")
def add_criticality(payload: CriticalityIn):
    create_criticality(payload.product_id, payload.level, payload.conformity_route, int(payload.notified_body_required), payload.notes)
    return {"status": "ok"}


@router.get("/criticality")
def get_criticality():
    return list_table("criticality").to_dict(orient="records")


@router.post("/assessments")
def add_assessment(payload: AssessmentIn):
    create_assessment(tuple(payload.model_dump().values()))
    return {"status": "ok"}


@router.get("/assessments")
def get_assessments():
    return list_table("assessments").to_dict(orient="records")


@router.post("/actions")
def add_action(payload: ActionIn):
    create_action(tuple(payload.model_dump().values()))
    return {"status": "ok"}


@router.get("/actions")
def get_actions():
    return list_table("actions").to_dict(orient="records")


@router.post("/evidence")
def add_evidence(payload: EvidenceIn):
    create_evidence(tuple(payload.model_dump().values()))
    return {"status": "ok"}


@router.get("/evidence")
def get_evidence():
    return list_table("evidence").to_dict(orient="records")


@router.post("/operations/vulnerabilities")
def add_vulnerability(payload: VulnerabilityIn):
    data = payload.model_dump()
    data["cvd_reported"] = int(data["cvd_reported"])
    create_vulnerability(tuple(data.values()))
    return {"status": "ok"}


@router.get("/operations/vulnerabilities")
def get_vulnerabilities():
    return list_table("vulnerabilities").to_dict(orient="records")


@router.post("/audit/findings")
def add_audit(payload: AuditIn):
    create_audit(tuple(payload.model_dump().values()))
    return {"status": "ok"}


@router.get("/audit/findings")
def get_audits():
    return list_table("audits").to_dict(orient="records")
