from cra_studio.repositories.requirements_repo import create_requirement, list_requirements

DEFAULT_REQUIREMENTS = [
    (
        "CRA-AI1-001",
        "Secure by default configuration",
        "Products shall be delivered with secure-by-default settings and hardening controls.",
        "Annex I.1",
        "security-by-design,hardening",
        "Configuration baseline, hardening checklist",
        "Config review + penetration test",
        "High",
        10,
        "1.0",
        "2026-01-01",
        "",
    ),
    (
        "CRA-AI2-001",
        "Coordinated vulnerability disclosure",
        "Operator shall maintain CVD policy, triage workflow, and patch delivery timeline.",
        "Annex I.2",
        "vulnerability-handling,operations",
        "CVD policy, ticket history, patch release notes",
        "Process audit + sampling",
        "Critical",
        10,
        "1.0",
        "2026-01-01",
        "",
    ),
]


def seed_default_requirements() -> None:
    if list_requirements(active_only=False).empty:
        for item in DEFAULT_REQUIREMENTS:
            create_requirement(item)
