import streamlit as st
import time
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide", page_title="Analyrix")

# ---------- DATABASE ----------
if "users_db" not in st.session_state:
    st.session_state.users_db = {}

# ---------- LANDING / LOGIN ----------
user_email = st.text_input("Enter your email to continue")

if not user_email:
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
        - ⚡ Fast scanning  
        - 🔒 Premium insights  
        """)

    st.divider()

    st.markdown(
        "[🚀 Get Pro Access ($19/month)](https://buy.stripe.com/14A14n6kuaaPffCdqoak000)"
    )

    st.stop()

# ---------- USER SETUP ----------
if user_email not in st.session_state.users_db:
    st.session_state.users_db[user_email] = {
        "plan": "free",
        "scans": 0,
        "last_reset": datetime.now()
    }

user = st.session_state.users_db[user_email]

# ---------- RESET ----------
if datetime.now() - user["last_reset"] > timedelta(hours=24):
    user["scans"] = 0
    user["last_reset"] = datetime.now()

# ---------- HEADER ----------
st.markdown(f"""
### 👤 {user_email}
Plan: **{user['plan'].upper()}**
Scans: {user['scans']} / {"∞" if user['plan']=="pro" else "3"}
""")

st.divider()

# ---------- UPGRADE ----------
if user["plan"] == "free":
    st.warning("🔒 Free plan: 3 scans per day")

    st.markdown(
        "[🚀 Upgrade to PRO](https://buy.stripe.com/14A14n6kuaaPffCdqoak000)"
    )

    if st.button("I have paid"):
        user["plan"] = "pro"
        st.success("PRO unlocked!")

# ---------- SCANNER ----------
scanner = VectorMarketScanner()

# ---------- DATA ----------
def get_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")

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
        line=dict(width=3)
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

# ---------- SCAN ----------
if st.button("🚀 Scan Market"):

    if user["plan"] == "free" and user["scans"] >= 3:
        st.error("🚫 Daily limit reached")
    else:
        with st.spinner("Scanning..."):
            time.sleep(1)
            results = scanner.scan_market(limit=10)
            user["scans"] += 1

            for i, r in enumerate(results):

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
                    **Entry:** {r['entry']}  
                    **Stop:** {r['stop_loss']}  
                    **Take Profit:** {r['take_profit']}
                    """)

                st.divider()
