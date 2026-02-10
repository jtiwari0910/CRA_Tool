from fastapi import FastAPI

from cra_studio.api.routers.inventory_router import router as inventory_router
from cra_studio.api.routers.program_router import router as program_router
from cra_studio.api.routers.reporting_router import router as reporting_router
from cra_studio.api.routers.requirements_router import router as requirements_router
from cra_studio.api.routers.workflow_router import router as workflow_router
from cra_studio.core.db import bootstrap_schema
from cra_studio.services.seed_service import seed_default_requirements


def create_app() -> FastAPI:
    app = FastAPI(title="CRA Deployment Studio API", version="2.0.0")

    @app.on_event("startup")
    def startup_event() -> None:
        bootstrap_schema()
        seed_default_requirements()

    app.include_router(program_router)
    app.include_router(inventory_router)
    app.include_router(requirements_router)
    app.include_router(workflow_router)
    app.include_router(reporting_router)
    return app


app = create_app()
