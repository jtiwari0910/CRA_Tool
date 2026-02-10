# CRA Deployment Studio

Python GUI application (Streamlit) for end-to-end CRA deployment management across OEMs, Tier-1 suppliers, dealers, and related entities.

## Features

- Full CRA workflow modules:
  - Setup & scope gate
  - Inventory and economic operator mapping
  - Criticality + conformity route planning
  - Requirement catalog management (add/remove/edit readiness)
  - Gap assessment and remediation planning
  - Evidence register and technical file indexing
  - Vulnerability/incident operations
  - Internal audit and CAPA tracking
  - Dashboards and PDF/Excel reporting
- Editable requirement catalog with version metadata (`effective_date`, `supersedes`)
- SQLite-backed persistence for local use

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- Designed to be migration-friendly toward FastAPI + React architecture later.
- Default requirement records are auto-seeded on first run.
