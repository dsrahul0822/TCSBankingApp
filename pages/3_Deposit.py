import streamlit as st
from src.validators import validate_positive_amount
from src.banking import deposit, calculate_balance, get_customer
from src.config import BANK_NAME, CURRENCY

st.title("➕ Deposit Money")

# --- Access control ---
if not st.session_state.get("logged_in"):
    st.error("❌ Please login first from the Login page.")
    st.stop()

customer_id = st.session_state.get("customer_id")
cust = get_customer(customer_id)

st.caption(f"{BANK_NAME} • Deposits for **{cust['customer_name']}** ({cust['account_no']})")

bal = calculate_balance(customer_id)
st.metric("Current Balance", f"{CURRENCY}{bal['current_balance']:,.2f}")

st.divider()

with st.form("deposit_form", clear_on_submit=True):
    amount = st.number_input("Deposit Amount", min_value=0.0, step=100.0, format="%.2f")
    reason = st.text_input("Reason", placeholder="Salary / Savings / Gift / Business income etc.")
    submitted = st.form_submit_button("✅ Submit Deposit", use_container_width=True)

if submitted:
    ok, msg = validate_positive_amount(amount)
    if not ok:
        st.error(msg)
        st.stop()

    txn = deposit(customer_id, amount, reason)
    st.success(f"Deposit successful! Transaction ID: **{txn['txn_id']}**")

    # show updated balance
    bal2 = calculate_balance(customer_id)
    st.metric("Updated Balance", f"{CURRENCY}{bal2['current_balance']:,.2f}")
    st.info("Go to **Mini Statement** page to view/download statement.")
