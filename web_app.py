import streamlit as st
import time
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide", page_title="Analyrix")

# ---------- SESSION ----------
if "users_db" not in st.session_state:
    st.session_state.users_db = {}

if "results" not in st.session_state:
    st.session_state.results = []

# ---------- LOGIN ----------
user_email = st.text_input("", placeholder="Enter your email to continue")

# ---------- USER ----------
if user_email and user_email not in st.session_state.users_db:
    st.session_state.users_db[user_email] = {
        "plan": "free",
        "scans": 0,
        "last_reset": datetime.now()
    }

user = st.session_state.users_db.get(user_email)

# ---------- RESET ----------
if user:
    if datetime.now() - user["last_reset"] > timedelta(hours=24):
        user["scans"] = 0
        user["last_reset"] = datetime.now()

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

# ---------- USER INFO ----------
if user:
    st.markdown(f"""
👤 {user_email}  
Plan: **{user['plan'].upper()}**  
Scans: {user['scans']} / {"∞" if user['plan']=="pro" else "3"}
""")

# ---------- UPGRADE ----------
if user and user["plan"] == "free":
    st.warning("🔒 Free plan: 3 scans/day")

    st.markdown(
        "[🚀 Upgrade to PRO](https://buy.stripe.com/14A14n6kuaaPffCdqoak000)"
    )

    if st.button("I have paid"):
        user["plan"] = "pro"

st.divider()

# ---------- SCANNER ----------
scanner = VectorMarketScanner()

if st.button("🚀 Scan Market"):

    if user and user["plan"] == "free" and user["scans"] >= 3:
        st.error("🚫 Daily limit reached")
    else:
        st.session_state.results = scanner.scan_market(limit=10)
        if user:
            user["scans"] += 1

# ---------- DATA ----------
def get_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
    except:
        dates = pd.date_range(end=pd.Timestamp.today(), periods=120)
        df = pd.DataFrame({
            "Date": dates,
            "Close": np.cumsum(np.random.randn(120)) + 100
        })

    df["Close"] = pd.Series(df["Close"]).astype(float)
    return df

def add_indicators(df):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()

    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9).mean()

    df = df.fillna(method="bfill").fillna(method="ffill")
    return df

# ---------- CHART ----------
def create_chart(ticker, signal):
    df = add_indicators(get_data(ticker))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Close"],
        mode="lines",
        name="Price",
        line=dict(width=3)
    ))

    fig.add_trace(go.Scatter(
        x=[df["Date"].iloc[-1]],
        y=[df["Close"].iloc[-1]],
        mode="markers+text",
        text=[signal],
        textposition="top center"
    ))

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["RSI"],
        name="RSI",
        yaxis="y2"
    ))

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
        height=500,
        yaxis=dict(title="Price"),
        yaxis2=dict(overlaying="y", side="right", position=0.95),
        yaxis3=dict(overlaying="y", side="right", position=0.85)
    )

    return fig

# ---------- RESULTS ----------
if st.session_state.results:

    for i, r in enumerate(st.session_state.results):

        st.markdown(f"""
### 📊 {r['ticker']}

**Signal:** {r['signal']}  
**Confidence:** {r['confidence']}%  
**Expected Move:** {r['expected_move']}%
""")

        if st.button(f"View {r['ticker']}", key=i):

            fig = create_chart(r["ticker"], r["signal"])
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
Entry: {r['entry']}  
Stop: {r['stop_loss']}  
Take Profit: {r['take_profit']}
""")

        st.divider()

# ---------- LOGIN MODAL ----------
if not user_email:

    st.markdown("## 🔒 Unlock Analyrix")

    st.info("""
**Free**
- 3 scans per day

**Pro**
- Unlimited scans  
- Full access  
- Better signals
""")

    st.warning("Enter your email above to continue")

    st.stop()
