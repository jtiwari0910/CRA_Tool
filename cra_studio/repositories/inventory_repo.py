from cra_studio.repositories.base_repo import execute, query_df


def create_product(organization_id: int, name: str, product_type: str, family: str, market: str) -> None:
    execute(
        "INSERT INTO products (organization_id, name, product_type, family, market) VALUES (?,?,?,?,?)",
        (organization_id, name, product_type, family, market),
    )


def list_products():
    return query_df("SELECT * FROM products ORDER BY id DESC")
