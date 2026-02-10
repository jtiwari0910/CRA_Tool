import io
import json
import sqlite3
from contextlib import closing
from datetime import date

import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DB_PATH = "cra_studio.db"


DEFAULT_REQUIREMENTS = [
    {
        "req_id": "CRA-AI1-001",
        "title": "Secure by default configuration",
        "text": "Products shall be delivered with secure-by-default settings and hardening controls.",
        "source": "Annex I.1",
        "tags": "security-by-design,hardening",
        "evidence_examples": "Configuration baseline, hardening checklist",
        "test_method": "Config review + penetration test",
        "severity": "High",
        "weight": 10,
        "version": "1.0",
        "effective_date": "2026-01-01",
        "supersedes": "",
    },
    {
        "req_id": "CRA-AI2-001",
        "title": "Coordinated vulnerability disclosure",
        "text": "Operator shall maintain CVD policy, triage workflow, and patch delivery timeline.",
        "source": "Annex I.2",
        "tags": "vulnerability-handling,operations",
        "evidence_examples": "CVD policy, ticket history, patch release notes",
        "test_method": "Process audit + sampling",
        "severity": "Critical",
        "weight": 10,
        "version": "1.0",
        "effective_date": "2026-01-01",
        "supersedes": "",
    },
    {
        "req_id": "CRA-AII-001",
        "title": "User information and instructions",
        "text": "Manufacturer shall provide security usage instructions and support period information.",
        "source": "Annex II",
        "tags": "user-information,documentation",
        "evidence_examples": "User manual, release notes, support statement",
        "test_method": "Document review",
        "severity": "Medium",
        "weight": 6,
        "version": "1.0",
        "effective_date": "2026-01-01",
        "supersedes": "",
    },
]


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
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
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                name TEXT NOT NULL,
                country TEXT,
                FOREIGN KEY(organization_id) REFERENCES organizations(id)
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER,
                site_id INTEGER,
                name TEXT NOT NULL,
                product_type TEXT,
                family TEXT,
                market TEXT,
                FOREIGN KEY(organization_id) REFERENCES organizations(id),
                FOREIGN KEY(site_id) REFERENCES sites(id)
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


def seed_requirements():
    with closing(get_conn()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM requirements")
        if cur.fetchone()[0] == 0:
            for req in DEFAULT_REQUIREMENTS:
                cur.execute(
                    """
                    INSERT INTO requirements (req_id, title, text, source, tags, evidence_examples, test_method, severity, weight, version, effective_date, supersedes)
                    VALUES (:req_id, :title, :text, :source, :tags, :evidence_examples, :test_method, :severity, :weight, :version, :effective_date, :supersedes)
                    """,
                    req,
                )
            conn.commit()


def run_query(query, params=()):
    with closing(get_conn()) as conn:
        return pd.read_sql_query(query, conn, params=params)


def execute(query, params=()):
    with closing(get_conn()) as conn:
        conn.execute(query, params)
        conn.commit()


def export_pdf(title, df):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, 810, title)
    c.setFont("Helvetica", 9)
    y = 790
    cols = [str(cn) for cn in df.columns[:6]]
    c.drawString(40, y, " | ".join(cols))
    y -= 15
    for _, row in df.head(40).iterrows():
        line = " | ".join([str(row[col])[:25] for col in cols])
        c.drawString(40, y, line)
        y -= 13
        if y < 40:
            c.showPage()
            y = 810
    c.save()
    buffer.seek(0)
    return buffer


def export_excel(sheets):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    buffer.seek(0)
    return buffer


def select_options(df, id_col="id", label_col="name"):
    if df.empty:
        return {}
    return {f"{r[label_col]} (#{r[id_col]})": int(r[id_col]) for _, r in df.iterrows()}


def main():
    st.set_page_config(page_title="CRA Deployment Studio", layout="wide")
    init_db()
    seed_requirements()

    st.title("CRA Deployment Studio")
    st.caption("End-to-end CRA deployment workflow for OEMs, Tier-1 suppliers, dealers, and related entities.")

    modules = [
        "Program Setup",
        "Product Inventory",
        "Applicability Gate",
        "Economic Operator Map",
        "Criticality & Conformity Route",
        "Requirements Library",
        "Gap Assessment",
        "Remediation Planner",
        "Evidence Register",
        "Conformity Assessment & Notified Body",
        "Vulnerability & Incidents",
        "Internal Audit",
        "Dashboards",
        "Reports / Exports",
    ]
    selected = st.sidebar.radio("Modules", modules)

    orgs = run_query("SELECT * FROM organizations ORDER BY id DESC")
    products = run_query("SELECT * FROM products ORDER BY id DESC")
    reqs = run_query("SELECT * FROM requirements WHERE active=1 ORDER BY req_id")

    if selected == "Program Setup":
        st.subheader("Phase 0 — Setup & Scope Gate")
        with st.form("org_form", clear_on_submit=True):
            cols = st.columns(3)
            name = cols[0].text_input("Organization name")
            org_type = cols[1].selectbox("Type", ["OEM", "Tier-1", "Dealer", "Authorized Representative", "Importer", "Distributor"])
            markets = cols[2].text_input("Markets", placeholder="EU, EEA")
            if st.form_submit_button("Create organization") and name:
                execute("INSERT INTO organizations (name, org_type, markets) VALUES (?,?,?)", (name, org_type, markets))
                st.success("Organization created")
                st.rerun()
        st.dataframe(orgs, use_container_width=True)

    elif selected == "Product Inventory":
        st.subheader("Phase 1 — Inventory")
        org_map = select_options(orgs)
        with st.form("product_form", clear_on_submit=True):
            cols = st.columns(5)
            org = cols[0].selectbox("Organization", options=list(org_map.keys())) if org_map else None
            name = cols[1].text_input("Product/System name")
            p_type = cols[2].selectbox("Type", ["ECU", "Vehicle Platform", "Backend Service", "Dealer System", "Plant OT"])
            family = cols[3].text_input("Family")
            market = cols[4].text_input("Market")
            if st.form_submit_button("Add product") and org and name:
                execute(
                    "INSERT INTO products (organization_id, name, product_type, family, market) VALUES (?,?,?,?,?)",
                    (org_map[org], name, p_type, family, market),
                )
                st.success("Product added")
                st.rerun()
        st.dataframe(products, use_container_width=True)

    elif selected == "Applicability Gate":
        st.subheader("Phase 0/1 — Product Applicability Gate")
        product_map = select_options(products)
        with st.form("applicability", clear_on_submit=True):
            p = st.selectbox("Product", options=list(product_map.keys())) if product_map else None
            in_scope = st.toggle("In CRA scope", value=True)
            reason = st.text_area("Exemption/justification")
            if st.form_submit_button("Save decision") and p:
                execute(
                    "INSERT INTO applicability (product_id, in_scope, justification, decision_date) VALUES (?,?,?,?)",
                    (product_map[p], int(in_scope), reason, str(date.today())),
                )
                st.success("Applicability decision recorded")
        st.dataframe(run_query("SELECT * FROM applicability ORDER BY id DESC"), use_container_width=True)

    elif selected == "Economic Operator Map":
        st.subheader("Phase 1 — Economic Operator Roles")
        product_map = select_options(products)
        with st.form("roles", clear_on_submit=True):
            p = st.selectbox("Product", options=list(product_map.keys())) if product_map else None
            role = st.selectbox("Role", ["Manufacturer", "Importer", "Distributor", "Authorized Representative"])
            owner = st.text_input("Responsible function/person")
            notes = st.text_area("Traceability expectations")
            if st.form_submit_button("Assign role") and p:
                execute(
                    "INSERT INTO economic_roles (product_id, role, owner, traceability_notes) VALUES (?,?,?,?)",
                    (product_map[p], role, owner, notes),
                )
                st.success("Role assigned")
        st.dataframe(run_query("SELECT * FROM economic_roles ORDER BY id DESC"), use_container_width=True)

    elif selected == "Criticality & Conformity Route":
        st.subheader("Phase 2 — Criticality and Annex VIII Route")
        product_map = select_options(products)
        with st.form("criticality", clear_on_submit=True):
            p = st.selectbox("Product", options=list(product_map.keys())) if product_map else None
            level = st.selectbox("Criticality", ["Default", "Important", "Critical"])
            route = st.selectbox("Conformity route", ["Module A", "Module B+C", "Module H", "Certification Scheme"])
            nb = st.toggle("Notified Body involvement", value=False)
            notes = st.text_area("Decision notes")
            if st.form_submit_button("Save classification") and p:
                execute(
                    "INSERT INTO criticality (product_id, level, conformity_route, notified_body_required, notes) VALUES (?,?,?,?,?)",
                    (product_map[p], level, route, int(nb), notes),
                )
                st.success("Classification saved")
        st.dataframe(run_query("SELECT * FROM criticality ORDER BY id DESC"), use_container_width=True)

    elif selected == "Requirements Library":
        st.subheader("Phase 3 — Requirement Catalog Manager")
        with st.form("req_add", clear_on_submit=True):
            cols = st.columns(4)
            req_id = cols[0].text_input("Requirement ID")
            title = cols[1].text_input("Title")
            source = cols[2].selectbox("CRA Source", ["Annex I.1", "Annex I.2", "Annex II", "Annex VII", "Annex VIII", "Economic Operator", "Market Surveillance"])
            severity = cols[3].selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            text = st.text_area("Requirement text")
            tags = st.text_input("Tags", placeholder="R155,21434,SBOM")
            evidence_examples = st.text_input("Evidence examples")
            test_method = st.text_input("Test method")
            v1, v2, v3 = st.columns(3)
            weight = v1.number_input("Weight", min_value=1, max_value=10, value=5)
            version = v2.text_input("Version", value="1.0")
            effective = v3.date_input("Effective date", value=date.today())
            supersedes = st.text_input("Supersedes")
            if st.form_submit_button("Add requirement") and req_id and title:
                execute(
                    """INSERT INTO requirements (req_id, title, text, source, tags, evidence_examples, test_method, severity, weight, version, effective_date, supersedes, active)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)""",
                    (req_id, title, text, source, tags, evidence_examples, test_method, severity, int(weight), version, str(effective), supersedes),
                )
                st.success("Requirement added")
                st.rerun()

        delete_id = st.text_input("Deactivate requirement by req_id")
        if st.button("Deactivate") and delete_id:
            execute("UPDATE requirements SET active=0 WHERE req_id=?", (delete_id,))
            st.success("Requirement deactivated")
            st.rerun()

        st.dataframe(reqs, use_container_width=True)

    elif selected == "Gap Assessment":
        st.subheader("Phase 3 — Gap Assessment")
        product_map = select_options(products)
        req_map = select_options(reqs, id_col="id", label_col="req_id")
        with st.form("assessment", clear_on_submit=True):
            c1, c2 = st.columns(2)
            p = c1.selectbox("Product", options=list(product_map.keys())) if product_map else None
            r = c2.selectbox("Requirement", options=list(req_map.keys())) if req_map else None
            c3, c4 = st.columns(2)
            maturity = c3.slider("Maturity score", 0, 5, 2)
            risk = c4.slider("Risk score", 1, 10, 5)
            gap = st.text_area("Gap summary")
            owner = st.text_input("Owner")
            status = st.selectbox("Status", ["Open", "In Progress", "Closed"])
            evidence_status = st.selectbox("Evidence status", ["Missing", "Partial", "Complete"])
            if st.form_submit_button("Save assessment") and p and r:
                execute(
                    "INSERT INTO assessments (product_id, requirement_id, maturity_score, risk_score, gap_summary, owner, status, evidence_status) VALUES (?,?,?,?,?,?,?,?)",
                    (product_map[p], req_map[r], maturity, risk, gap, owner, status, evidence_status),
                )
                st.success("Assessment saved")
        st.dataframe(run_query("SELECT * FROM assessments ORDER BY id DESC"), use_container_width=True)

    elif selected == "Remediation Planner":
        st.subheader("Phase 4 — Remediation Work Items")
        product_map = select_options(products)
        req_map = select_options(reqs, id_col="id", label_col="req_id")
        with st.form("actions", clear_on_submit=True):
            p = st.selectbox("Product", options=list(product_map.keys())) if product_map else None
            r = st.selectbox("Requirement", options=list(req_map.keys())) if req_map else None
            title = st.text_input("Action title")
            owner = st.text_input("Owner")
            due = st.date_input("Due date", value=date.today())
            status = st.selectbox("Status", ["Open", "In Progress", "Blocked", "Done"])
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            notes = st.text_area("Notes")
            if st.form_submit_button("Create action") and p and r and title:
                execute(
                    "INSERT INTO actions (product_id, requirement_id, title, owner, due_date, status, priority, notes) VALUES (?,?,?,?,?,?,?,?)",
                    (product_map[p], req_map[r], title, owner, str(due), status, priority, notes),
                )
                st.success("Action added")
        st.dataframe(run_query("SELECT * FROM actions ORDER BY id DESC"), use_container_width=True)

    elif selected == "Evidence Register":
        st.subheader("Phase 5 — Evidence & Technical File Builder")
        product_map = select_options(products)
        req_map = select_options(reqs, id_col="id", label_col="req_id")
        with st.form("evidence", clear_on_submit=True):
            p = st.selectbox("Product", options=list(product_map.keys())) if product_map else None
            r = st.selectbox("Requirement", options=list(req_map.keys())) if req_map else None
            name = st.text_input("Artifact name")
            a_type = st.selectbox("Type", ["SBOM", "Risk Assessment", "Test Report", "User Docs", "DoC", "Other"])
            link = st.text_input("Link or file path")
            score = st.slider("Completeness score", 0, 100, 60)
            if st.form_submit_button("Register evidence") and p and r and name:
                execute(
                    "INSERT INTO evidence (product_id, requirement_id, artifact_name, artifact_type, link_or_path, uploaded_on, completeness_score) VALUES (?,?,?,?,?,?,?)",
                    (product_map[p], req_map[r], name, a_type, link, str(date.today()), score),
                )
                st.success("Evidence recorded")
        st.dataframe(run_query("SELECT * FROM evidence ORDER BY id DESC"), use_container_width=True)

    elif selected == "Conformity Assessment & Notified Body":
        st.subheader("Phase 5 — Conformity Planning")
        conformity = run_query(
            """
            SELECT p.name as product, c.level, c.conformity_route, c.notified_body_required, c.notes
            FROM criticality c JOIN products p ON p.id = c.product_id
            ORDER BY c.id DESC
            """
        )
        st.dataframe(conformity, use_container_width=True)
        st.info("Use this view to prepare Module A/B+C/H route records and Notified Body readiness evidence mapping.")

    elif selected == "Vulnerability & Incidents":
        st.subheader("Phase 6 — Operational Compliance")
        product_map = select_options(products)
        with st.form("vuln", clear_on_submit=True):
            p = st.selectbox("Product", options=list(product_map.keys())) if product_map else None
            vid = st.text_input("Vulnerability ID")
            sev = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            stat = st.selectbox("Status", ["Open", "Triaged", "Fix In Progress", "Resolved"])
            detected = st.date_input("Detected on", value=date.today())
            target_fix = st.date_input("Target fix date", value=date.today())
            cvd = st.toggle("Reported through CVD workflow", value=True)
            notes = st.text_area("Notes")
            if st.form_submit_button("Record vulnerability") and p and vid:
                execute(
                    "INSERT INTO vulnerabilities (product_id, vuln_id, severity, status, detected_on, target_fix_date, cvd_reported, notes) VALUES (?,?,?,?,?,?,?,?)",
                    (product_map[p], vid, sev, stat, str(detected), str(target_fix), int(cvd), notes),
                )
                st.success("Vulnerability recorded")
        st.dataframe(run_query("SELECT * FROM vulnerabilities ORDER BY id DESC"), use_container_width=True)

    elif selected == "Internal Audit":
        st.subheader("Phase 7 — Internal Audit & CAPA")
        product_map = select_options(products)
        with st.form("audit", clear_on_submit=True):
            p = st.selectbox("Product", options=list(product_map.keys())) if product_map else None
            adate = st.date_input("Audit date", value=date.today())
            auditor = st.text_input("Auditor")
            finding = st.text_area("Finding")
            capa_owner = st.text_input("CAPA owner")
            capa_status = st.selectbox("CAPA status", ["Open", "In Progress", "Closed"])
            conf = st.selectbox("Confidentiality", ["Internal", "Restricted", "Confidential"])
            if st.form_submit_button("Save audit finding") and p:
                execute(
                    "INSERT INTO audits (product_id, audit_date, auditor, finding, capa_owner, capa_status, confidentiality_level) VALUES (?,?,?,?,?,?,?)",
                    (product_map[p], str(adate), auditor, finding, capa_owner, capa_status, conf),
                )
                st.success("Audit record saved")
        st.dataframe(run_query("SELECT * FROM audits ORDER BY id DESC"), use_container_width=True)

    elif selected == "Dashboards":
        st.subheader("Core Dashboards")
        assessed = run_query("SELECT COUNT(DISTINCT product_id) as c FROM assessments")
        total_products = run_query("SELECT COUNT(*) as c FROM products")
        gaps_open = run_query("SELECT COUNT(*) as c FROM assessments WHERE status != 'Closed'")
        high_risk = run_query("SELECT COUNT(*) as c FROM assessments WHERE risk_score >= 8")
        due_90 = run_query("SELECT COUNT(*) as c FROM actions WHERE due_date <= date('now', '+90 day') AND status != 'Done'")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Products", int(total_products.iloc[0]["c"]))
        c2.metric("Products Assessed", int(assessed.iloc[0]["c"]))
        c3.metric("Open Gaps", int(gaps_open.iloc[0]["c"]))
        c4.metric("High Risk Findings", int(high_risk.iloc[0]["c"]))
        c5.metric("Due in 90d", int(due_90.iloc[0]["c"]))

        st.markdown("#### Engineering View")
        eng = run_query("SELECT evidence_status, COUNT(*) cnt FROM assessments GROUP BY evidence_status")
        if not eng.empty:
            st.bar_chart(eng.set_index("evidence_status"))

        st.markdown("#### Supplier/Dealer View")
        supplier = run_query("SELECT role, COUNT(*) cnt FROM economic_roles GROUP BY role")
        if not supplier.empty:
            st.bar_chart(supplier.set_index("role"))

    elif selected == "Reports / Exports":
        st.subheader("PDF + Excel reporting")
        inventory_df = run_query("SELECT * FROM products")
        gaps_df = run_query("SELECT * FROM assessments")
        actions_df = run_query("SELECT * FROM actions")
        evidence_df = run_query("SELECT * FROM evidence")

        report_type = st.selectbox(
            "PDF report",
            [
                "Gap report",
                "Remediation plan",
                "Technical documentation index",
                "Vulnerability status report",
                "Audit report",
            ],
        )
        mapping = {
            "Gap report": gaps_df,
            "Remediation plan": actions_df,
            "Technical documentation index": evidence_df,
            "Vulnerability status report": run_query("SELECT * FROM vulnerabilities"),
            "Audit report": run_query("SELECT * FROM audits"),
        }

        pdf_bytes = export_pdf(report_type, mapping[report_type])
        st.download_button("Download PDF", data=pdf_bytes, file_name=f"{report_type.replace(' ', '_').lower()}.pdf", mime="application/pdf")

        excel_bytes = export_excel(
            {
                "Inventory": inventory_df,
                "Gaps": gaps_df,
                "Actions": actions_df,
                "Evidence": evidence_df,
            }
        )
        st.download_button(
            "Download Excel Pack",
            data=excel_bytes,
            file_name="cra_deployment_studio_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        technical_file = {
            "annex_vii_pack": [
                "Product Description",
                "Risk Assessment",
                "SBOM",
                "Test Reports",
                "Update Policy",
                "User Instructions",
                "EU Declaration of Conformity Draft Fields",
            ]
        }
        st.code(json.dumps(technical_file, indent=2), language="json")


if __name__ == "__main__":
    main()
