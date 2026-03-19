import streamlit as st
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide")

# --- LOGIN SIMULATION ---
if "paid" not in st.session_state:
    st.session_state.paid = False

# --- HEADER ---
st.title("🚀 Quantara AI Terminal")

# --- PAYWALL ---
if not st.session_state.paid:
    st.warning("🔒 Free version: limited access")

    if st.button("Unlock Pro ($19/month)"):
        st.session_state.paid = True

# --- SCANNER ---
scanner = VectorMarketScanner()

if st.button("Scan Market"):
    results = scanner.scan_market(limit=20)

    # LIMIT FREE USERS
    if not st.session_state.paid:
        results = results[:3]

    for r in results:
        st.subheader(r["ticker"])
        st.write(
            f"{r['signal']} | Conf: {r['confidence']}% | "
            f"Move: {r['expected_move']}% | Risk: {r['risk']}"
        )

        st.write(f"Entry: {r['entry']}")

        with st.expander("🧠 Why this trade"):
            st.write(r["reason"])

        st.divider()
