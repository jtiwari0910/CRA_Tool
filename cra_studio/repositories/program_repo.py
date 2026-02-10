from cra_studio.repositories.base_repo import execute, query_df


def create_organization(name: str, org_type: str, markets: str) -> None:
    execute(
        "INSERT INTO organizations (name, org_type, markets) VALUES (?,?,?)",
        (name, org_type, markets),
    )


def list_organizations():
    return query_df("SELECT * FROM organizations ORDER BY id DESC")
