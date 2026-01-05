import streamlit as st
from src.config import BANK_NAME, LOGO_PATH

st.set_page_config(page_title=BANK_NAME, page_icon="🏦", layout="wide")

# session defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

# Sidebar (status)
with st.sidebar:
    st.markdown("### 🏦 State Bank of Python")
    if st.session_state.logged_in:
        st.success(f"Logged in as: **{st.session_state.user_id}**")
        st.caption(f"Customer ID: {st.session_state.customer_id}")
    else:
        st.warning("Not logged in")

# Header
col1, col2 = st.columns([1, 6], vertical_alignment="center")
with col1:
    try:
        st.image(LOGO_PATH, use_container_width=True)
    except Exception:
        st.markdown("## 🏦")
with col2:
    st.title(BANK_NAME)
    st.caption("Excel-based mini banking app • Streamlit Cloud ready")

st.divider()
st.info("Use the left sidebar to open pages: Login → Summary → Deposit → Withdraw → Mini Statement.")
