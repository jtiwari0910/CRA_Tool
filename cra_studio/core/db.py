import sqlite3
from contextlib import closing

DB_PATH = "cra_studio.db"


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def bootstrap_schema() -> None:
    with closing(get_conn()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                org_type TEXT NOT NULL,
                markets TEXT,
                created_at TEXT DEFAULT CURRENT_DATE
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                name TEXT NOT NULL,
                product_type TEXT,
                family TEXT,
                market TEXT,
                FOREIGN KEY(organization_id) REFERENCES organizations(id)
            );
            CREATE TABLE IF NOT EXISTS applicability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                in_scope INTEGER NOT NULL,
                justification TEXT,
                decision_date TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            CREATE TABLE IF NOT EXISTS economic_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                role TEXT,
                owner TEXT,
                traceability_notes TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            CREATE TABLE IF NOT EXISTS criticality (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                level TEXT,
                conformity_route TEXT,
                notified_body_required INTEGER,
                notes TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                req_id TEXT UNIQUE,
                title TEXT,
                text TEXT,
                source TEXT,
                tags TEXT,
                evidence_examples TEXT,
                test_method TEXT,
                severity TEXT,
                weight INTEGER,
                version TEXT,
                effective_date TEXT,
                supersedes TEXT,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                requirement_id INTEGER,
                maturity_score INTEGER,
                risk_score INTEGER,
                gap_summary TEXT,
                owner TEXT,
                status TEXT,
                evidence_status TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id),
                FOREIGN KEY(requirement_id) REFERENCES requirements(id)
            );
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                requirement_id INTEGER,
                title TEXT,
                owner TEXT,
                due_date TEXT,
                status TEXT,
                priority TEXT,
                notes TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id),
                FOREIGN KEY(requirement_id) REFERENCES requirements(id)
            );
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                requirement_id INTEGER,
                artifact_name TEXT,
                artifact_type TEXT,
                link_or_path TEXT,
                uploaded_on TEXT,
                completeness_score INTEGER,
                FOREIGN KEY(product_id) REFERENCES products(id),
                FOREIGN KEY(requirement_id) REFERENCES requirements(id)
            );
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                vuln_id TEXT,
                severity TEXT,
                status TEXT,
                detected_on TEXT,
                target_fix_date TEXT,
                cvd_reported INTEGER,
                notes TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                audit_date TEXT,
                auditor TEXT,
                finding TEXT,
                capa_owner TEXT,
                capa_status TEXT,
                confidentiality_level TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            """
        )
        conn.commit()
