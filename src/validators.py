# src/validators.py

from __future__ import annotations


def validate_positive_amount(amount: float) -> tuple[bool, str]:
    try:
        amt = float(amount)
    except Exception:
        return False, "Amount must be a number."

    if amt <= 0:
        return False, "Amount must be greater than 0."

    return True, ""
def validate_withdraw_amount(amount: float, balance: float) -> tuple[bool, str]:
    ok, msg = validate_positive_amount(amount)
    if not ok:
        return False, msg

    if float(amount) > float(balance):
        return False, "Insufficient balance. Withdraw amount cannot exceed current balance."

    return True, ""
