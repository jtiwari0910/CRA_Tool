from cra_studio.repositories.base_repo import execute, query_df


def create_applicability(product_id: int, in_scope: int, justification: str, decision_date: str) -> None:
    execute(
        "INSERT INTO applicability (product_id, in_scope, justification, decision_date) VALUES (?,?,?,?)",
        (product_id, in_scope, justification, decision_date),
    )


def create_economic_role(product_id: int, role: str, owner: str, notes: str) -> None:
    execute(
        "INSERT INTO economic_roles (product_id, role, owner, traceability_notes) VALUES (?,?,?,?)",
        (product_id, role, owner, notes),
    )


def create_criticality(product_id: int, level: str, route: str, nb_required: int, notes: str) -> None:
    execute(
        "INSERT INTO criticality (product_id, level, conformity_route, notified_body_required, notes) VALUES (?,?,?,?,?)",
        (product_id, level, route, nb_required, notes),
    )


def create_assessment(payload: tuple) -> None:
    execute(
        "INSERT INTO assessments (product_id, requirement_id, maturity_score, risk_score, gap_summary, owner, status, evidence_status) VALUES (?,?,?,?,?,?,?,?)",
        payload,
    )


def create_action(payload: tuple) -> None:
    execute(
        "INSERT INTO actions (product_id, requirement_id, title, owner, due_date, status, priority, notes) VALUES (?,?,?,?,?,?,?,?)",
        payload,
    )


def create_evidence(payload: tuple) -> None:
    execute(
        "INSERT INTO evidence (product_id, requirement_id, artifact_name, artifact_type, link_or_path, uploaded_on, completeness_score) VALUES (?,?,?,?,?,?,?)",
        payload,
    )


def create_vulnerability(payload: tuple) -> None:
    execute(
        "INSERT INTO vulnerabilities (product_id, vuln_id, severity, status, detected_on, target_fix_date, cvd_reported, notes) VALUES (?,?,?,?,?,?,?,?)",
        payload,
    )


def create_audit(payload: tuple) -> None:
    execute(
        "INSERT INTO audits (product_id, audit_date, auditor, finding, capa_owner, capa_status, confidentiality_level) VALUES (?,?,?,?,?,?,?)",
        payload,
    )


def list_table(table_name: str):
    return query_df(f"SELECT * FROM {table_name} ORDER BY id DESC")
