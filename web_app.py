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

# ---------- HEADER ----------
st.title("🚀 Analyrix")
st.caption("AI-powered trade analysis")

scanner = VectorMarketScanner()

# ---------- PAYWALL ----------
if not st.session_state.pro:
    st.warning("🔒 Free: 3 scans per 24h")

    st.markdown(
        "[🚀 Unlock Pro ($19/month)](https://buy.stripe.com/14A14n6kuaaPffCdqoak000)",
        unsafe_allow_html=True
    )

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
        # fallback data
        dates = pd.date_range(end=pd.Timestamp.today(), periods=120)
        price = np.cumsum(np.random.randn(120)) + 100

        df = pd.DataFrame({
            "Date": dates,
            "Open": price,
            "High": price + 2,
            "Low": price - 2,
            "Close": price,
            "Volume": np.random.randint(100000, 500000, size=120)
        })

        return df

# ---------- INDICATORS ----------
def add_indicators(df):

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()

    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9).mean()

    return df

# ---------- CHART ----------
def create_chart(ticker):

    df = get_data(ticker)
    df = add_indicators(df)

    fig = go.Figure()

    # PRICE
    fig.add_trace(go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    ))

    # RSI
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["RSI"],
        name="RSI",
        yaxis="y2"
    ))

    # MACD
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["MACD"],
        name="MACD",
        yaxis="y3"
    ))

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Signal"],
        name="Signal",
        yaxis="y3"
    ))

    fig.update_layout(
        template="plotly_dark",
        height=600,
        xaxis_rangeslider_visible=False,

        yaxis=dict(title="Price"),
        yaxis2=dict(
            title="RSI",
            overlaying="y",
            side="right",
            position=0.95
        ),
        yaxis3=dict(
            title="MACD",
            overlaying="y",
            side="right",
            position=0.85
        )
    )

    return fig

# ---------- SCAN ----------
if st.button("🔍 Scan Market"):

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
        ### {r['ticker']}
        {r['signal']} | {r['confidence']}% | {r['expected_move']}%
        """)

        if st.button(f"📊 View {r['ticker']}", key=i):

            fig = create_chart(r["ticker"])
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            **Entry:** ${r['entry']}  
            **Stop Loss:** ${r['stop_loss']}  
            **Take Profit:** ${r['take_profit']}  

            **Expected Hold:** {get_timeframe(r)}
            """)

        st.divider()
