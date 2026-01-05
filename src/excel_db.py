# src/excel_db.py

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Dict

import pandas as pd

from .config import DATA_FILE_PATH


LOCK_FILE = DATA_FILE_PATH + ".lock"


@contextmanager
def file_lock(timeout: int = 10):
    """
    Simple lock to prevent simultaneous writes (Streamlit reruns can overlap writes).
    """
    start = time.time()
    while os.path.exists(LOCK_FILE):
        if time.time() - start > timeout:
            raise RuntimeError("Excel file is busy/locked. Try again.")
        time.sleep(0.2)

    try:
        with open(LOCK_FILE, "w") as f:
            f.write("locked")
        yield
    finally:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)


def read_sheet(sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(DATA_FILE_PATH, sheet_name=sheet_name)


def read_all_sheets() -> Dict[str, pd.DataFrame]:
    xl = pd.ExcelFile(DATA_FILE_PATH)
    return {name: xl.parse(name) for name in xl.sheet_names}


def overwrite_sheet(sheet_name: str, df: pd.DataFrame) -> None:
    """
    Replace a sheet safely (works with pandas 2.x).
    """
    with file_lock():
        if not os.path.exists(DATA_FILE_PATH):
            # create new workbook with this one sheet
            with pd.ExcelWriter(DATA_FILE_PATH, engine="openpyxl", mode="w") as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            return

        # append mode + replace the target sheet
        with pd.ExcelWriter(
            DATA_FILE_PATH,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace"
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def append_row(sheet_name: str, row: dict) -> None:
    df = read_sheet(sheet_name)

    if df.empty:
        df = pd.DataFrame(columns=list(row.keys()))

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    overwrite_sheet(sheet_name, df)
