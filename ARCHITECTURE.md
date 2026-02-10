# CRA Deployment Studio — Microservice Architecture

## 1) High-Level Architecture

The solution is split into **small domain services** that can run independently (or together behind one FastAPI process during local development):

- **Program Service**: organizations, sites, setup/scope context
- **Inventory Service**: products and product metadata
- **Applicability Service**: CRA scope decisions and exemption justifications
- **Economic Operator Service**: manufacturer/importer/distributor/AR mappings
- **Conformity Service**: criticality classification and Annex VIII route planning
- **Requirements Service**: editable/versioned requirement catalog
- **Assessment Service**: maturity/risk gap assessment
- **Remediation Service**: action tracking and closure
- **Evidence Service**: technical file artifacts and completeness
- **Operations Service**: vulnerability/incident workflow
- **Audit Service**: internal audit findings + CAPA
- **Reporting Service**: dashboard KPIs + PDF/Excel exports

A **GUI Orchestrator** (Streamlit) talks to the API layer and composes end-to-end workflow views.

## 2) Component View

- `cra_studio/core/db.py`
  - SQLite connection + schema bootstrap
- `cra_studio/repositories/*.py`
  - Low-level CRUD for each table
- `cra_studio/services/*.py`
  - Domain logic per microservice
- `cra_studio/api/routers/*.py`
  - REST endpoints, one router per service
- `cra_studio/api/app.py`
  - API composition entrypoint (acts as local API gateway)
- `gui/streamlit_app.py`
  - GUI app with module navigation and report downloads
- `gui/api_client.py`
  - API integration helper used by GUI

## 3) Deployment Modes

1. **Local single-process mode**: run one FastAPI app (all routers included), and Streamlit GUI.
2. **Microservice mode**: deploy each router/service as independent app by extracting router to dedicated service process.

## 4) Data Stores

- Default: SQLite (`cra_studio.db`) for local deployment.
- Future: PostgreSQL adapter by replacing DB connector and SQL dialect edges.

## 5) API Contracts (Representative)

- `POST /program/organizations`
- `POST /inventory/products`
- `POST /applicability/decisions`
- `POST /requirements`
- `POST /assessments`
- `POST /actions`
- `POST /evidence`
- `POST /operations/vulnerabilities`
- `POST /audit/findings`
- `GET /reporting/dashboard`
- `GET /reporting/export/excel`
- `GET /reporting/export/pdf?report_type=gap`

## 6) Why this qualifies as microservice architecture-based

- Functionality is split by bounded domain into independent service modules.
- Small, single-purpose files are used for database, repositories, business logic, and transport layer.
- API contracts isolate GUI from implementation, enabling independent evolution/deployment.
