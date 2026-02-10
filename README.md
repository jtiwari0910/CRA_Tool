# CRA Deployment Studio (Microservice-Architecture Based)

A Python CRA deployment platform for automotive OEMs, Tier-1s, dealers, and related entities.

## What changed

This version is refactored from a monolith into a **microservice architecture-based** implementation:

- Domain routers/services separated into independent modules.
- API gateway composition via FastAPI (`cra_studio/api/app.py`).
- Streamlit GUI as a separate orchestrator client (`gui/streamlit_app.py`).
- Report generation and DB logic split into dedicated service/repository files.

See full architecture in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Directory layout

- `cra_studio/core/` — DB bootstrap and connectivity
- `cra_studio/repositories/` — table-level persistence helpers
- `cra_studio/services/` — business and reporting logic
- `cra_studio/api/routers/` — REST endpoints per domain service
- `gui/` — Streamlit GUI and API client
- `run_api.py` — start API gateway
- `app.py` — GUI launcher compatibility entrypoint

## Run

```bash
pip install -r requirements.txt
python run_api.py
streamlit run gui/streamlit_app.py
```

## CRA workflow coverage

- Setup & Scope gate
- Inventory & operator mapping
- Criticality + conformity route
- Requirements catalog (add/remove/version)
- Gap assessment and remediation
- Evidence/technical file registry
- Vulnerability and incident ops
- Internal audit + CAPA
- KPI dashboards
- PDF/Excel exports
