# src/auth.py

from __future__ import annotations
import pandas as pd
from typing import Optional, Tuple

from .excel_db import read_sheet
from .config import SHEET_LOGIN


def validate_login(user_id: str, password: str) -> Tuple[bool, Optional[str]]:
    """
    Returns: (is_valid, customer_id)
    Plain text check (as requested).
    """
    user_id = (user_id or "").strip()
    password = (password or "").strip()

    if not user_id or not password:
        return False, None

    df = read_sheet(SHEET_LOGIN)

    # Ensure columns exist
    required = {"user_id", "password", "customer_id"}
    if not required.issubset(set(df.columns)):
        return False, None

    match = df[(df["user_id"] == user_id) & (df["password"] == password)]
    if match.empty:
        return False, None

    customer_id = str(match.iloc[0]["customer_id"])
    return True, customer_id


def logout() -> None:
    """Clear login session."""
    import streamlit as st
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.customer_id = None
