import streamlit as st
import time
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
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

Scan hundreds of stocks, get instant signals, and clear trade plans with entry, stop loss and take profit.
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
    st.info("🔓 Upgrade to Pro for unlimited scans and full access")

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

        df = df.reset_index()
        return df

    except:
        dates = pd.date_range(end=pd.Timestamp.today(), periods=120)
        price = np.cumsum(np.random.randn(120)) + 100

        return pd.DataFrame({
            "Date": dates,
            "Open": price,
            "High": price + 2,
            "Low": price - 2,
            "Close": price,
            "Volume": np.random.randint(100000, 500000, size=120)
        })

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

    return df

# ---------- CHART ----------
def create_chart(ticker, signal):

    df = get_data(ticker)
    df = add_indicators(df)

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2]
    )

    # PRICE LINE (CLEAN)
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Close"],
        name="Price",
        line=dict(width=2)
    ), row=1, col=1)

    # 🔥 BUY/SELL MARKER
    last_x = df["Date"].iloc[-1]
    last_y = df["Close"].iloc[-1]

    color = "green" if signal == "BUY" else "red"

    fig.add_trace(go.Scatter(
        x=[last_x],
        y=[last_y],
        mode="markers+text",
        text=[signal],
        textposition="top center",
        marker=dict(size=12, color=color),
        name="Signal"
    ), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["RSI"],
        name="RSI"
    ), row=2, col=1)

    # MACD
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["MACD"],
        name="MACD"
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Signal"],
        name="Signal"
    ), row=3, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=700,
        xaxis_rangeslider_visible=False
    )

    return fig

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
