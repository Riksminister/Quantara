import streamlit as st
import time
import pandas as pd
import random
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide", page_title="Quantara AI")

st.markdown("# 🚀 Quantara AI Terminal")
st.caption("AI scanning the market in real-time")

scanner = VectorMarketScanner()

if st.button("🔍 Scan Market"):

    with st.spinner("AI scanning 7000+ stocks..."):
        time.sleep(1.5)

        results = scanner.scan_market(limit=20)

    st.success("Scan complete ✅")

    for i, r in enumerate(results):

        st.markdown(f"""
        ### #{i+1} {r['ticker']}
        **Signal:** {r['signal']}  
        **Confidence:** {r['confidence']}%  
        **Move:** {r['expected_move']}%  
        """)

        # --- FAKE CHART ---
        if st.button(f"Show chart {r['ticker']}", key=i):

            prices = [r["entry"]]

            for _ in range(30):
                change = random.uniform(-2, 2)
                prices.append(prices[-1] * (1 + change/100))

            chart_df = pd.DataFrame({"price": prices})

            st.line_chart(chart_df)

        with st.expander("🧠 Why this trade"):
            st.write(r["reason"])

        st.divider()
