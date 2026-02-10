from datetime import date

import pandas as pd
import streamlit as st

from gui.api_client import get, get_binary, patch, post


MODULES = [
    "Program Setup",
    "Product Inventory",
    "Applicability Gate",
    "Economic Operator Map",
    "Criticality & Conformity Route",
    "Requirements Library",
    "Gap Assessment",
    "Remediation Planner",
    "Evidence Register",
    "Vulnerability & Incidents",
    "Internal Audit",
    "Dashboards",
    "Reports / Exports",
]


def to_df(data):
    return pd.DataFrame(data if isinstance(data, list) else [data])


def option_map(rows, key="name"):
    if not rows:
        return {}
    return {f"{row.get(key)} (#{row['id']})": row["id"] for row in rows}


def main():
    st.set_page_config(page_title="CRA Deployment Studio", layout="wide")
    st.title("CRA Deployment Studio")
    selected = st.sidebar.radio("Modules", MODULES)

    orgs = get("/program/organizations")
    products = get("/inventory/products")
    requirements = get("/requirements", params={"active_only": True})

    if selected == "Program Setup":
        with st.form("org"):
            name = st.text_input("Organization name")
            org_type = st.selectbox("Type", ["OEM", "Tier-1", "Dealer", "Authorized Representative", "Importer", "Distributor"])
            markets = st.text_input("Markets")
            if st.form_submit_button("Create") and name:
                post("/program/organizations", {"name": name, "org_type": org_type, "markets": markets})
                st.success("Saved")
                st.rerun()
        st.dataframe(to_df(orgs), use_container_width=True)

    elif selected == "Product Inventory":
        omap = option_map(orgs)
        with st.form("product"):
            org_choice = st.selectbox("Organization", list(omap.keys())) if omap else None
            name = st.text_input("Product")
            p_type = st.selectbox("Type", ["ECU", "Vehicle Platform", "Backend Service", "Dealer System", "Plant OT"])
            family = st.text_input("Family")
            market = st.text_input("Market")
            if st.form_submit_button("Add") and org_choice and name:
                post("/inventory/products", {"organization_id": omap[org_choice], "name": name, "product_type": p_type, "family": family, "market": market})
                st.success("Saved")
                st.rerun()
        st.dataframe(to_df(products), use_container_width=True)

    elif selected == "Requirements Library":
        with st.form("req"):
            req_id = st.text_input("Req ID")
            title = st.text_input("Title")
            text = st.text_area("Text")
            source = st.selectbox("Source", ["Annex I.1", "Annex I.2", "Annex II", "Annex VII", "Annex VIII", "Economic Operator", "Market Surveillance"])
            tags = st.text_input("Tags")
            evidence_examples = st.text_input("Evidence examples")
            test_method = st.text_input("Test method")
            severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            weight = st.number_input("Weight", 1, 10, 5)
            version = st.text_input("Version", value="1.0")
            effective_date = st.date_input("Effective", value=date.today())
            supersedes = st.text_input("Supersedes")
            if st.form_submit_button("Add requirement") and req_id and title:
                post(
                    "/requirements",
                    {
                        "req_id": req_id,
                        "title": title,
                        "text": text,
                        "source": source,
                        "tags": tags,
                        "evidence_examples": evidence_examples,
                        "test_method": test_method,
                        "severity": severity,
                        "weight": int(weight),
                        "version": version,
                        "effective_date": str(effective_date),
                        "supersedes": supersedes,
                    },
                )
                st.success("Saved")
                st.rerun()
        deactivate = st.text_input("Deactivate req_id")
        if st.button("Deactivate") and deactivate:
            patch(f"/requirements/{deactivate}/deactivate")
            st.rerun()
        st.dataframe(to_df(requirements), use_container_width=True)

    elif selected == "Dashboards":
        dashboard = get("/reporting/dashboard")
        cols = st.columns(5)
        cols[0].metric("Products", dashboard.get("products", 0))
        cols[1].metric("Assessed", dashboard.get("products_assessed", 0))
        cols[2].metric("Open Gaps", dashboard.get("open_gaps", 0))
        cols[3].metric("High Risk", dashboard.get("high_risk_findings", 0))
        cols[4].metric("Due 90d", dashboard.get("due_90_days", 0))

    elif selected == "Reports / Exports":
        pdf_type = st.selectbox("PDF", ["gap", "remediation", "technical_file", "vulnerability", "audit"])
        st.download_button("Download PDF", data=get_binary("/reporting/export/pdf", {"report_type": pdf_type}), file_name=f"{pdf_type}.pdf", mime="application/pdf")
        st.download_button(
            "Download Excel",
            data=get_binary("/reporting/export/excel"),
            file_name="cra_deployment_studio_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    else:
        st.info("This module is available via API endpoints and can be expanded with dedicated UI forms similarly.")


if __name__ == "__main__":
    main()
