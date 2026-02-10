from pydantic import BaseModel


class OrganizationIn(BaseModel):
    name: str
    org_type: str
    markets: str = ""


class ProductIn(BaseModel):
    organization_id: int
    name: str
    product_type: str
    family: str = ""
    market: str = ""


class ApplicabilityIn(BaseModel):
    product_id: int
    in_scope: bool
    justification: str = ""
    decision_date: str


class EconomicRoleIn(BaseModel):
    product_id: int
    role: str
    owner: str = ""
    traceability_notes: str = ""


class CriticalityIn(BaseModel):
    product_id: int
    level: str
    conformity_route: str
    notified_body_required: bool
    notes: str = ""


class RequirementIn(BaseModel):
    req_id: str
    title: str
    text: str
    source: str
    tags: str = ""
    evidence_examples: str = ""
    test_method: str = ""
    severity: str
    weight: int
    version: str
    effective_date: str
    supersedes: str = ""


class AssessmentIn(BaseModel):
    product_id: int
    requirement_id: int
    maturity_score: int
    risk_score: int
    gap_summary: str = ""
    owner: str = ""
    status: str
    evidence_status: str


class ActionIn(BaseModel):
    product_id: int
    requirement_id: int
    title: str
    owner: str = ""
    due_date: str
    status: str
    priority: str
    notes: str = ""


class EvidenceIn(BaseModel):
    product_id: int
    requirement_id: int
    artifact_name: str
    artifact_type: str
    link_or_path: str = ""
    uploaded_on: str
    completeness_score: int


class VulnerabilityIn(BaseModel):
    product_id: int
    vuln_id: str
    severity: str
    status: str
    detected_on: str
    target_fix_date: str
    cvd_reported: bool
    notes: str = ""


class AuditIn(BaseModel):
    product_id: int
    audit_date: str
    auditor: str = ""
    finding: str = ""
    capa_owner: str = ""
    capa_status: str
    confidentiality_level: str
