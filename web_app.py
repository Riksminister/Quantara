import streamlit as st
import pandas as pd
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide", page_title="Quantara AI")

scanner = VectorMarketScanner()  # reload fix

# --- HEADER ---
st.markdown("""
# 🚀 Quantara AI Terminal
Find high-probability trades instantly
""")

# --- SIDEBAR ---
st.sidebar.title("💰 Account")

if "balance" not in st.session_state:
    st.session_state.balance = 1000

profit = st.sidebar.number_input("Add Profit ($)", value=0.0)

if st.sidebar.button("Update Balance"):
    st.session_state.balance += profit

st.sidebar.metric("Balance", f"${st.session_state.balance:.2f}")

# --- SCAN BUTTON ---
if st.button("🔍 Scan Market"):
    results = scanner.scan_market(limit=20)

    st.subheader("📊 AI Trade Opportunities")

    for r in results:
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 2])

            with col1:
                st.markdown(f"### {r['ticker']}")

            with col2:
                st.write(
                    f"{r['signal']} | Conf: {r['confidence']}% | "
                    f"Move: {r['expected_move']}% | Risk: {r['risk']}"
                )

            with col3:
                st.write(f"Entry: {r['entry']}")

            with st.expander("🧠 Why this trade"):
                st.write(r.get("reason", "No explanation available"))

            st.divider()
