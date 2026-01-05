# src/pdf_statement.py

from __future__ import annotations

from io import BytesIO
from datetime import datetime

import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)

from .config import BANK_NAME, LOGO_PATH, CURRENCY


def _safe_str(x) -> str:
    return "" if x is None else str(x)


def generate_statement_pdf(
    customer: pd.Series,
    txns: pd.DataFrame,
    balances: dict,
    period_from: datetime | None = None,
    period_to: datetime | None = None,
) -> bytes:
    """
    Returns a PDF as bytes (ReportLab).
    Professional-ish statement layout.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
        title=f"{BANK_NAME} - Statement",
        author=BANK_NAME,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        spaceAfter=8,
    )
    subtle_style = ParagraphStyle(
        "Subtle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
    )
    normal = styles["Normal"]

    story = []

    # --- Header with logo + bank name ---
    header_tbl_data = []
    logo_cell = ""
    try:
        logo = Image(LOGO_PATH, width=2.8 * cm, height=2.8 * cm)
        logo.hAlign = "LEFT"
        logo_cell = logo
    except Exception:
        logo_cell = Paragraph("🏦", title_style)

    header_right = [
        Paragraph(f"<b>{BANK_NAME}</b>", title_style),
        Paragraph("Account Statement", styles["Heading2"]),
        Paragraph(f"Generated on: {_safe_str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}", subtle_style),
    ]

    if period_from and period_to:
        header_right.append(
            Paragraph(
                f"Statement Period: {_safe_str(period_from.strftime('%Y-%m-%d'))} to {_safe_str(period_to.strftime('%Y-%m-%d'))}",
                subtle_style,
            )
        )

    header_tbl_data.append([logo_cell, header_right])

    header_tbl = Table(header_tbl_data, colWidths=[3.2 * cm, 13.8 * cm])
    header_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 10))

    # --- Customer details block ---
    cust_rows = [
        ["Customer Name", _safe_str(customer.get("customer_name"))],
        ["Customer ID", _safe_str(customer.get("customer_id"))],
        ["Account No", _safe_str(customer.get("account_no"))],
        ["Account Type", _safe_str(customer.get("account_type"))],
        ["Email", _safe_str(customer.get("email"))],
        ["Phone", _safe_str(customer.get("phone"))],
        ["City", _safe_str(customer.get("city"))],
    ]

    cust_tbl = Table(cust_rows, colWidths=[5.0 * cm, 12.0 * cm])
    cust_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(cust_tbl)
    story.append(Spacer(1, 10))

    # --- Summary KPIs ---
    opening = float(balances.get("opening_balance", 0) or 0)
    dep = float(balances.get("total_deposit", 0) or 0)
    wd = float(balances.get("total_withdraw", 0) or 0)
    current = float(balances.get("current_balance", 0) or 0)

    summary_data = [
        ["Opening Balance", f"{CURRENCY}{opening:,.2f}",
         "Total Deposits", f"{CURRENCY}{dep:,.2f}"],
        ["Total Withdrawals", f"{CURRENCY}{wd:,.2f}",
         "Current Balance", f"{CURRENCY}{current:,.2f}"],
    ]
    summary_tbl = Table(summary_data, colWidths=[4.0 * cm, 4.5 * cm, 4.0 * cm, 4.5 * cm])
    summary_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F6FF")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D6E0FF")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D6E0FF")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(summary_tbl)
    story.append(Spacer(1, 12))

    # --- Transactions table ---
    story.append(Paragraph("<b>Transaction Details</b>", styles["Heading3"]))
    story.append(Spacer(1, 6))

    if txns is None or txns.empty:
        story.append(Paragraph("No transactions available for the selected period.", normal))
    else:
        tx = txns.copy()

        # normalize fields
        tx["txn_date"] = pd.to_datetime(tx["txn_date"], errors="coerce")
        tx["txn_date"] = tx["txn_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        tx["amount"] = pd.to_numeric(tx["amount"], errors="coerce").fillna(0.0)
        tx["balance_after_txn"] = pd.to_numeric(tx["balance_after_txn"], errors="coerce").fillna(0.0)

        tx = tx[["txn_id", "txn_date", "txn_type", "amount", "reason", "balance_after_txn"]]

        table_data = [["Txn ID", "Date", "Type", "Amount", "Reason", "Balance"]]
        for _, r in tx.iterrows():
            table_data.append([
                _safe_str(r["txn_id"]),
                _safe_str(r["txn_date"]),
                _safe_str(r["txn_type"]),
                f"{CURRENCY}{float(r['amount']):,.2f}",
                _safe_str(r["reason"])[:40],  # keep tidy
                f"{CURRENCY}{float(r['balance_after_txn']):,.2f}",
            ])

        txn_tbl = Table(
            table_data,
            colWidths=[2.2 * cm, 3.8 * cm, 2.2 * cm, 2.6 * cm, 4.2 * cm, 3.0 * cm],
            repeatRows=1
        )
        txn_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3B73")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),

            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),

            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(txn_tbl)

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "This is a system-generated statement and does not require a signature.",
        subtle_style
    ))

    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
