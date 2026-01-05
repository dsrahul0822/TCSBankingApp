import streamlit as st
from src.auth import validate_login, logout
from src.config import BANK_NAME, LOGO_PATH

st.title("🔐 Login")
st.caption(f"Welcome to {BANK_NAME}. Please login to continue.")

# If already logged in
if st.session_state.get("logged_in"):
    st.success(f"Already logged in as **{st.session_state.user_id}** (Customer: {st.session_state.customer_id})")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    with col2:
        st.info("Now open **Customer Summary** from the sidebar.")
    st.stop()

# Logo (optional on login page)
try:
    st.image(LOGO_PATH, width=220)
except Exception:
    pass

with st.form("login_form", clear_on_submit=False):
    user_id = st.text_input("User ID", placeholder="e.g., rahul01")
    password = st.text_input("Password", type="password", placeholder="e.g., rahul123")
    submitted = st.form_submit_button("Login", use_container_width=True)

if submitted:
    ok, customer_id = validate_login(user_id, password)
    if ok:
        st.session_state.logged_in = True
        st.session_state.user_id = user_id.strip()
        st.session_state.customer_id = customer_id
        st.success("✅ Login successful!")
        st.info("Open **Customer Summary** from the sidebar.")
        st.rerun()
    else:
        st.error("❌ Invalid User ID or Password.")
