import io
from typing import Dict

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def make_pdf(title: str, df: pd.DataFrame) -> bytes:
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
    return buffer.read()


def make_excel(sheets: Dict[str, pd.DataFrame]) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    buffer.seek(0)
    return buffer.read()
