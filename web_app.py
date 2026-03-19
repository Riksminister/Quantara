import streamlit as st
import time
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide", page_title="Quantara AI")

# --- HEADER ---
st.markdown("# 🚀 Quantara AI Terminal")
st.caption("AI scanning the market in real-time")

# --- PAYWALL ---
if "paid" not in st.session_state:
    st.session_state.paid = False

if not st.session_state.paid:
    st.warning("🔒 Free version: limited access")

    if st.button("Unlock Pro ($19/month)"):
        st.session_state.paid = True

# --- SCANNER ---
scanner = VectorMarketScanner()

if st.button("🔍 Scan Market"):

    with st.spinner("AI scanning 7000+ stocks..."):
        time.sleep(1.5)  # fake realism

        results = scanner.scan_market(limit=50)

    st.success("Scan complete ✅")

    # LIMIT FREE USERS
    if not st.session_state.paid:
        results = results[:5]

    st.subheader("📊 Top AI Opportunities")

    for i, r in enumerate(results):

        color = "green" if r["signal"] == "BUY" else "orange"

        st.markdown(f"""
        ### #{i+1} {r['ticker']}
        **Signal:** :{color}[{r['signal']}]  
        **Confidence:** {r['confidence']}%  
        **Expected Move:** {r['expected_move']}%  
        **Risk:** {r['risk']}  
        **Entry:** ${r['entry']}
        """)

        with st.expander("🧠 Why this trade"):
            st.write(r["reason"])

        st.divider()
