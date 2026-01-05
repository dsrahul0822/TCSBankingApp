import streamlit as st
from src.banking import get_customer, calculate_balance
from src.config import BANK_NAME, CURRENCY, LOGO_PATH

st.title("📊 Customer Summary")

# --- Access control ---
if not st.session_state.get("logged_in"):
    st.error("❌ Please login first from the Login page.")
    st.stop()

customer_id = st.session_state.get("customer_id")

# --- Fetch data ---
cust = get_customer(customer_id)
bal = calculate_balance(customer_id)

# --- Header card ---
col1, col2 = st.columns([1, 4], vertical_alignment="center")

with col1:
    try:
        st.image(LOGO_PATH, width=160)
    except Exception:
        st.markdown("### 🏦")

with col2:
    st.subheader(f"Welcome, {cust['customer_name']} 👋")
    st.caption(f"{BANK_NAME} • Account No: **{cust['account_no']}** • Type: **{cust['account_type']}**")

st.divider()

# --- KPIs ---
k1, k2, k3, k4 = st.columns(4)

k1.metric("Opening Balance", f"{CURRENCY}{bal['opening_balance']:,.2f}")
k2.metric("Total Deposits", f"{CURRENCY}{bal['total_deposit']:,.2f}")
k3.metric("Total Withdrawals", f"{CURRENCY}{bal['total_withdraw']:,.2f}")
k4.metric("Current Balance", f"{CURRENCY}{bal['current_balance']:,.2f}")

st.divider()

# --- Customer details section ---
st.subheader("👤 Customer Details")
c1, c2, c3 = st.columns(3)

with c1:
    st.write(f"**Customer ID:** {cust['customer_id']}")
    st.write(f"**Name:** {cust['customer_name']}")
    st.write(f"**City:** {cust['city']}")

with c2:
    st.write(f"**Email:** {cust['email']}")
    st.write(f"**Phone:** {cust['phone']}")
    st.write(f"**Account Type:** {cust['account_type']}")

with c3:
    st.write(f"**Account No:** {cust['account_no']}")
    st.write("**Status:** Active ✅")
    st.write("**KYC:** Completed ✅")

st.info("Next: Go to **Deposit** or **Withdraw** page from sidebar to create transactions.")
