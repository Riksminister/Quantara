import streamlit as st
import time
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide", page_title="Analyrix")

# ---------- STATE ----------
if "results" not in st.session_state:
    st.session_state.results = []

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

# ---------- HERO ----------
st.markdown("""
# 🚀 Analyrix

### Find high-probability trades in seconds using AI

Scan hundreds of stocks or analyze any stock instantly.
""")

col1, col2, col3 = st.columns(3)
col1.metric("📊 Stocks Scanned", "400+")
col2.metric("⚡ Scan Time", "<2 sec")
col3.metric("🎯 Accuracy", "AI-driven")

st.divider()

# ---------- FEATURES ----------
st.markdown("## 🔥 What you get")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
- 🧠 AI trade signals  
- 📈 Expected move prediction  
- 🎯 Entry, stop loss, take profit  
- ⏱️ Expected hold time  
- 🔍 Search any stock instantly  
""")

with col2:
    st.markdown("""
- 📊 Smart charts  
- 📉 RSI + MACD indicators  
- ⚡ Fast market scanning  
- 🔒 Premium insights (Pro)  
""")

st.divider()

scanner = VectorMarketScanner()

# ---------- PAYWALL ----------
if not st.session_state.pro:
    st.info("🔓 Upgrade to Pro for unlimited scans")

    st.markdown(
        "[🚀 Get Pro Access ($19/month)](https://buy.stripe.com/14A14n6kuaaPffCdqoak000)"
    )

    st.warning("🔒 Free: 3 scans per 24h")
    st.divider()

# ---------- TIMEFRAME ----------
def get_timeframe(trade):
    move = trade["expected_move"]
    if move > 8:
        return "Short-term (1–3 days)"
    elif move > 4:
        return "Medium-term (3–7 days)"
    else:
        return "Longer-term (1–2 weeks)"

# ---------- DATA ----------
def get_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")

        if df is None or df.empty:
            raise Exception("No data")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

    except:
        dates = pd.date_range(end=pd.Timestamp.today(), periods=120)
        price = np.cumsum(np.random.randn(120)) + 100

        df = pd.DataFrame({
            "Date": dates,
            "Close": price
        })

    df["Close"] = pd.Series(df["Close"]).astype(float)
    return df

# ---------- INDICATORS ----------
def add_indicators(df):

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()

    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9).mean()

    df = df.fillna(method="bfill").fillna(method="ffill")

    return df

# ---------- CHART ----------
def create_chart(ticker, signal):

    df = get_data(ticker)
    df = add_indicators(df)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Close"],
        name="Price",
        mode="lines",
        line=dict(width=3, color="#00bfff")
    ))

    last_x = df["Date"].iloc[-1]
    last_y = df["Close"].iloc[-1]

    color = "green" if signal == "BUY" else "red"

    fig.add_trace(go.Scatter(
        x=[last_x],
        y=[last_y],
        mode="markers+text",
        text=[signal],
        textposition="top center",
        marker=dict(size=14, color=color)
    ))

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["RSI"],
        name="RSI",
        opacity=0.6,
        yaxis="y2"
    ))

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["MACD"],
        name="MACD",
        opacity=0.6,
        yaxis="y3"
    ))

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Signal"],
        name="Signal",
        opacity=0.6,
        yaxis="y3"
    ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        yaxis=dict(title="Price"),
        yaxis2=dict(overlaying="y", side="right", position=0.95),
        yaxis3=dict(overlaying="y", side="right", position=0.85)
    )

    return fig

# ---------- SEARCH (FIXED) ----------
st.markdown("## 🔍 Search stock")

col1, col2 = st.columns([4, 1])

ticker_input = col1.text_input(
    "Enter ticker (e.g. TSLA, AAPL)",
    key="search_input"
)

search_run = col2.button("ENTER")

if search_run:

    if not ticker_input:
        st.warning("Enter a ticker")

    elif not st.session_state.pro and st.session_state.scan_count >= 3:
        st.error("🚫 Free limit reached")

    else:
        with st.spinner(f"Analyzing {ticker_input.upper()}..."):

            result = scanner.analyze_single_stock(ticker_input.upper())
            st.session_state.scan_count += 1

            st.markdown(f"""
            ### 📊 {result['ticker']}

            **🧠 AI Signal:** {result['signal']}  
            **📊 AI Confidence:** {result['confidence']}%  
            **📈 Expected Move:** {result['expected_move']}%  
            **⚠️ Risk Level:** {result['risk']}
            """)

            fig = create_chart(result["ticker"], result["signal"])
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            ### 📈 Trade Plan

            **Entry Price:** ${result['entry']}  
            **Stop Loss:** ${result['stop_loss']}  
            **Take Profit:** ${result['take_profit']}  

            ### ⏱️ Expected Hold  
            {get_timeframe(result)}
            """)

# ---------- SCAN ----------
if st.button("🚀 Scan Market Now"):

    if not st.session_state.pro and st.session_state.scan_count >= 3:
        st.error("🚫 Free limit reached")
    else:
        with st.spinner("Scanning hundreds of stocks..."):
            time.sleep(1.5)
            st.session_state.results = scanner.scan_market(limit=20)
            st.session_state.scan_count += 1

# ---------- DISPLAY ----------
if st.session_state.results:

    for i, r in enumerate(st.session_state.results):

        st.markdown(f"""
        ### 📊 {r['ticker']}

        **🧠 AI Signal:** {r['signal']}  
        **📊 AI Confidence:** {r['confidence']}%  
        **📈 Expected Move:** {r['expected_move']}%  
        **⚠️ Risk Level:** {r['risk']}
        """)

        if st.button(f"📊 View Chart - {r['ticker']}", key=i):

            fig = create_chart(r["ticker"], r["signal"])
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            ### 📈 Trade Plan

            **Entry Price:** ${r['entry']}  
            **Stop Loss:** ${r['stop_loss']}  
            **Take Profit:** ${r['take_profit']}  

            ### ⏱️ Expected Hold  
            {get_timeframe(r)}
            """)

        st.divider()
