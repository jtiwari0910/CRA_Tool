from cra_studio.repositories.base_repo import execute, query_df


def create_requirement(payload: tuple) -> None:
    execute(
        """
        INSERT INTO requirements (req_id, title, text, source, tags, evidence_examples, test_method, severity, weight, version, effective_date, supersedes, active)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)
        """,
        payload,
    )


def deactivate_requirement(req_id: str) -> None:
    execute("UPDATE requirements SET active=0 WHERE req_id=?", (req_id,))


def list_requirements(active_only: bool = True):
    if active_only:
        return query_df("SELECT * FROM requirements WHERE active=1 ORDER BY req_id")
    return query_df("SELECT * FROM requirements ORDER BY req_id")
