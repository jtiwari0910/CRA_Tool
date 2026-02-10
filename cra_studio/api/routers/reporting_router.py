from fastapi import APIRouter
from fastapi.responses import Response

from cra_studio.repositories.base_repo import query_df
from cra_studio.services.report_service import make_excel, make_pdf

router = APIRouter(prefix="/reporting", tags=["reporting"])


@router.get("/dashboard")
def get_dashboard():
    total_products = int(query_df("SELECT COUNT(*) c FROM products").iloc[0]["c"])
    assessed = int(query_df("SELECT COUNT(DISTINCT product_id) c FROM assessments").iloc[0]["c"])
    open_gaps = int(query_df("SELECT COUNT(*) c FROM assessments WHERE status != 'Closed'").iloc[0]["c"])
    high_risk = int(query_df("SELECT COUNT(*) c FROM assessments WHERE risk_score >= 8").iloc[0]["c"])
    due_90 = int(query_df("SELECT COUNT(*) c FROM actions WHERE due_date <= date('now', '+90 day') AND status != 'Done'").iloc[0]["c"])
    return {
        "products": total_products,
        "products_assessed": assessed,
        "open_gaps": open_gaps,
        "high_risk_findings": high_risk,
        "due_90_days": due_90,
    }


@router.get("/export/pdf")
def export_pdf(report_type: str = "gap"):
    table_map = {
        "gap": "assessments",
        "remediation": "actions",
        "technical_file": "evidence",
        "vulnerability": "vulnerabilities",
        "audit": "audits",
    }
    table = table_map.get(report_type, "assessments")
    df = query_df(f"SELECT * FROM {table}")
    payload = make_pdf(f"{report_type.title()} Report", df)
    return Response(content=payload, media_type="application/pdf")


@router.get("/export/excel")
def export_excel():
    payload = make_excel(
        {
            "Inventory": query_df("SELECT * FROM products"),
            "Gaps": query_df("SELECT * FROM assessments"),
            "Actions": query_df("SELECT * FROM actions"),
            "Evidence": query_df("SELECT * FROM evidence"),
        }
    )
    return Response(
        content=payload,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
