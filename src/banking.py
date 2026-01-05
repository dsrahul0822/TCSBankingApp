# src/banking.py

from __future__ import annotations
import pandas as pd
from datetime import datetime
from .excel_db import append_row

from .excel_db import read_sheet
from .config import SHEET_CUSTOMERS, SHEET_TXNS


def get_customer(customer_id: str) -> pd.Series:
    """Return the customer row as a pandas Series."""
    df = read_sheet(SHEET_CUSTOMERS)
    row = df[df["customer_id"] == customer_id]
    if row.empty:
        raise ValueError(f"Customer not found: {customer_id}")
    return row.iloc[0]


def get_transactions(customer_id: str) -> pd.DataFrame:
    """Return all transactions for a customer (sorted latest first)."""
    df = read_sheet(SHEET_TXNS)

    # If sheet is empty (no txns yet), return empty df with expected columns
    if df.empty:
        return pd.DataFrame(columns=[
            "txn_id", "customer_id", "txn_date", "txn_type",
            "amount", "reason", "balance_after_txn"
        ])

    df = df[df["customer_id"] == customer_id].copy()

    # sort by date if possible
    if "txn_date" in df.columns:
        df["txn_date"] = pd.to_datetime(df["txn_date"], errors="coerce")
        df = df.sort_values("txn_date", ascending=False)

    return df


def calculate_balance(customer_id: str) -> dict:
    """
    Returns a dict:
    {
      opening_balance,
      total_deposit,
      total_withdraw,
      current_balance
    }
    """
    cust = get_customer(customer_id)
    opening = float(cust.get("opening_balance", 0) or 0)

    txns = get_transactions(customer_id)

    if txns.empty:
        return {
            "opening_balance": opening,
            "total_deposit": 0.0,
            "total_withdraw": 0.0,
            "current_balance": opening
        }

    txns["amount"] = pd.to_numeric(txns["amount"], errors="coerce").fillna(0)

    deposits = float(txns[txns["txn_type"] == "DEPOSIT"]["amount"].sum())
    withdraws = float(txns[txns["txn_type"] == "WITHDRAW"]["amount"].sum())

    current = opening + deposits - withdraws

    return {
        "opening_balance": opening,
        "total_deposit": deposits,
        "total_withdraw": withdraws,
        "current_balance": current
    }

def _next_txn_id(txn_df: pd.DataFrame) -> str:
    """
    Generates TXN000001 style IDs.
    If sheet empty -> TXN000001.
    """
    if txn_df.empty or "txn_id" not in txn_df.columns:
        return "TXN000001"

    ids = txn_df["txn_id"].dropna().astype(str).tolist()
    nums = []
    for x in ids:
        if x.startswith("TXN"):
            tail = x.replace("TXN", "")
            if tail.isdigit():
                nums.append(int(tail))
    nxt = (max(nums) + 1) if nums else 1
    return f"TXN{nxt:06d}"


def deposit(customer_id: str, amount: float, reason: str) -> dict:
    """
    Creates a DEPOSIT transaction and appends into Excel.
    Returns the created transaction row (dict).
    """
    # current balance before txn
    bal = calculate_balance(customer_id)
    current = float(bal["current_balance"])

    txn_df = read_sheet(SHEET_TXNS)
    txn_id = _next_txn_id(txn_df)

    new_balance = current + float(amount)

    row = {
        "txn_id": txn_id,
        "customer_id": customer_id,
        "txn_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "txn_type": "DEPOSIT",
        "amount": float(amount),
        "reason": (reason or "").strip(),
        "balance_after_txn": float(new_balance),
    }

    append_row(SHEET_TXNS, row)
    return row

def withdraw(customer_id: str, amount: float, reason: str) -> dict:
    """
    Creates a WITHDRAW transaction and appends into Excel.
    Returns the created transaction row (dict).
    """
    bal = calculate_balance(customer_id)
    current = float(bal["current_balance"])

    txn_df = read_sheet(SHEET_TXNS)
    txn_id = _next_txn_id(txn_df)

    new_balance = current - float(amount)

    row = {
        "txn_id": txn_id,
        "customer_id": customer_id,
        "txn_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "txn_type": "WITHDRAW",
        "amount": float(amount),
        "reason": (reason or "").strip(),
        "balance_after_txn": float(new_balance),
    }

    append_row(SHEET_TXNS, row)
    return row
