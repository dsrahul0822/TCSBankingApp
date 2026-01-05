import streamlit as st
from src.validators import validate_withdraw_amount
from src.banking import withdraw, calculate_balance, get_customer
from src.config import BANK_NAME, CURRENCY

st.title("➖ Withdraw Money")

# --- Access control ---
if not st.session_state.get("logged_in"):
    st.error("❌ Please login first from the Login page.")
    st.stop()

customer_id = st.session_state.get("customer_id")
cust = get_customer(customer_id)

st.caption(f"{BANK_NAME} • Withdrawals for **{cust['customer_name']}** ({cust['account_no']})")

bal = calculate_balance(customer_id)
current_balance = float(bal["current_balance"])
st.metric("Current Balance", f"{CURRENCY}{current_balance:,.2f}")

st.divider()

with st.form("withdraw_form", clear_on_submit=True):
    amount = st.number_input("Withdraw Amount", min_value=0.0, step=100.0, format="%.2f")
    reason = st.text_input("Reason", placeholder="Rent / Groceries / EMI / Cash / Emergency etc.")
    submitted = st.form_submit_button("✅ Submit Withdrawal", use_container_width=True)

if submitted:
    ok, msg = validate_withdraw_amount(amount, current_balance)
    if not ok:
        st.error(msg)
        st.stop()

    txn = withdraw(customer_id, amount, reason)
    st.success(f"Withdrawal successful! Transaction ID: **{txn['txn_id']}**")

    bal2 = calculate_balance(customer_id)
    st.metric("Updated Balance", f"{CURRENCY}{bal2['current_balance']:,.2f}")
    st.info("Go to **Mini Statement** page to view/download statement.")
