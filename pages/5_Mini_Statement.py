import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.banking import get_customer, get_transactions, calculate_balance
from src.pdf_statement import generate_statement_pdf
from src.config import BANK_NAME

st.title("🧾 Mini Statement")

# --- Access control ---
if not st.session_state.get("logged_in"):
    st.error("❌ Please login first from the Login page.")
    st.stop()

customer_id = st.session_state.get("customer_id")
cust = get_customer(customer_id)
bal = calculate_balance(customer_id)

st.caption(f"{BANK_NAME} • Statement for **{cust['customer_name']}** ({cust['account_no']})")
st.metric("Current Balance", f"₹{bal['current_balance']:,.2f}")

st.divider()

# --- Load all txns ---
txns = get_transactions(customer_id)

# Ensure datetime conversion for filtering
if not txns.empty:
    txns["txn_date"] = pd.to_datetime(txns["txn_date"], errors="coerce")

# --- Filters ---
st.subheader("Filters")

col1, col2, col3 = st.columns([1.2, 1.2, 1])

default_to = datetime.now().date()
default_from = (datetime.now() - timedelta(days=30)).date()

with col1:
    date_from = st.date_input("From", value=default_from)
with col2:
    date_to = st.date_input("To", value=default_to)
with col3:
    txn_type = st.selectbox("Type", ["ALL", "DEPOSIT", "WITHDRAW"])

filtered = txns.copy()
if not filtered.empty:
    # date range filter
    start_dt = datetime.combine(date_from, datetime.min.time())
    end_dt = datetime.combine(date_to, datetime.max.time())

    filtered = filtered[(filtered["txn_date"] >= start_dt) & (filtered["txn_date"] <= end_dt)]

    # type filter
    if txn_type != "ALL":
        filtered = filtered[filtered["txn_type"] == txn_type]

    filtered = filtered.sort_values("txn_date", ascending=False)

st.divider()

st.subheader("Transaction List")

if filtered.empty:
    st.info("No transactions found for the selected filters.")
else:
    show_df = filtered.copy()
    show_df["txn_date"] = show_df["txn_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    show_df["amount"] = pd.to_numeric(show_df["amount"], errors="coerce").fillna(0.0)
    show_df["balance_after_txn"] = pd.to_numeric(show_df["balance_after_txn"], errors="coerce").fillna(0.0)

    show_df = show_df[["txn_id", "txn_date", "txn_type", "amount", "reason", "balance_after_txn"]]
    st.dataframe(show_df, use_container_width=True)

st.divider()

# --- PDF download ---
st.subheader("Download Statement")

period_from = datetime.combine(date_from, datetime.min.time())
period_to = datetime.combine(date_to, datetime.max.time())

pdf_bytes = generate_statement_pdf(
    customer=cust,
    txns=filtered if not filtered.empty else filtered,
    balances=bal,
    period_from=period_from,
    period_to=period_to,
)

filename = f"statement_{cust['account_no']}_{date_from}_to_{date_to}.pdf"

st.download_button(
    label="📄 Download PDF Statement",
    data=pdf_bytes,
    file_name=filename,
    mime="application/pdf",
    use_container_width=True
)
