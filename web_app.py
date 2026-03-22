import streamlit as st
import time
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide", page_title="Analyrix")

# ---------- STATE ----------
if "results" not in st.session_state:
    st.session_state.results = []

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None

if "pro" not in st.session_state:
    st.session_state.pro = False

if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0

if "last_scan_reset" not in st.session_state:
    st.session_state.last_scan_reset = datetime.now()

# ---------- RESET ----------
if datetime.now() - st.session_state.last_scan_reset > timedelta(hours=24):
    st.session_state.scan_count = 0
    st.session_state.last_scan_reset = datetime.now()

# ---------- HEADER ----------
st.markdown("# 🚀 Analyrix")
st.caption("AI-powered trade analysis")

scanner = VectorMarketScanner()

# ---------- PAYWALL ----------
if not st.session_state.pro:
    st.warning("🔒 Free: 3 scans per 24h")

    st.markdown(
        "[🚀 Unlock Pro ($19/month)](https://buy.stripe.com/14A14n6kuaaPffCdqoak000)",
        unsafe_allow_html=True
    )

# ---------- SCAN ----------
if st.button("🔍 Scan Market"):

    if not st.session_state.pro and st.session_state.scan_count >= 3:
        st.error("🚫 Limit reached")
    else:
        with st.spinner("Scanning hundreds of stocks..."):
            time.sleep(1.5)
            st.session_state.results = scanner.scan_market(limit=20)
            st.session_state.selected_index = None
            st.session_state.scan_count += 1

# ---------- CHART ----------
def create_chart(ticker):

    df = yf.download(ticker, period="6mo", interval="1d")

    if df.empty:
        return None

    df = df.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Ohlc(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        increasing_line_color="green",
        decreasing_line_color="red"
    ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_rangeslider_visible=False
    )

    return fig

# ---------- DISPLAY ----------
if st.session_state.results:

    def rank_trade(trade):
        score = {"BUY": 3, "WATCH": 2, "AVOID": 1}
        return (score.get(trade["signal"], 0), trade["expected_move"])

    results = sorted(
        st.session_state.results,
        key=rank_trade,
        reverse=True
    )

    if not st.session_state.pro:
        results = results[:3]

    for i, r in enumerate(results):

        st.markdown(f"""
        ### #{i+1} {r['ticker']}
        {r['signal']} | {r['confidence']}% | {r['expected_move']}%
        """)

        if st.button("📊 View Chart", key=f"btn{i}"):
            st.session_state.selected_index = i

        if st.session_state.selected_index == i:

            fig = create_chart(r["ticker"])
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            st.write(f"Entry: ${r['entry']}")
            st.write(f"Stop Loss: ${r['stop_loss']}")
            st.write(f"Take Profit: ${r['take_profit']}")

        st.divider()
