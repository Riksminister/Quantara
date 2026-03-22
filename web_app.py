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

# ---------- INPUT ----------
user_email = st.text_input("", placeholder="")

# ---------- USER SETUP ----------
if user_email and user_email not in st.session_state.users_db:
    st.session_state.users_db[user_email] = {
        "plan": "free",
        "scans": 0,
        "last_reset": datetime.now()
    }

user = st.session_state.users_db.get(user_email, None)

# ---------- RESET ----------
if user:
    if datetime.now() - user["last_reset"] > timedelta(hours=24):
        user["scans"] = 0
        user["last_reset"] = datetime.now()

# ---------- HEADER ----------
st.markdown("# 🚀 Analyrix")
st.caption("AI-powered trade analysis")

if user:
    st.markdown(f"""
    👤 {user_email}  
    Plan: **{user['plan'].upper()}**  
    Scans: {user['scans']} / {"∞" if user['plan']=="pro" else "3"}
    """)

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

# ---------- DISPLAY ----------
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

# ---------- OVERLAY ----------
if not user_email:

    st.markdown("""
    <style>
    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.85);
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="overlay">
        <div>
            <h1>🔒 Unlock Analyrix</h1>
            <p>See full AI trade signals and charts</p>

            <h3>Free</h3>
            <p>3 scans per day</p>

            <h3>Pro</h3>
            <p>Unlimited scans<br>Full access</p>

            <br>
            <p>Enter email above to continue</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()
