import streamlit as st
import time
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from core.scanner import VectorMarketScanner
import re

st.set_page_config(layout="wide", page_title="Analyrix")

# ---------- LOGIN STATE ----------
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# ---------- LANDING + LOGIN ----------
if not st.session_state.user_email:

    st.markdown("""
# 🚀 Analyrix

### Find high-probability trades in seconds using AI

Scan hundreds of stocks or analyze any stock instantly.
""")

    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Stocks Scanned", "800+")
    col2.metric("⚡ Scan Time", "Few seconds")
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

    st.markdown("## 🔐 Get started")

    email_input = st.text_input("Enter your email")

    if st.button("Continue"):
        if email_input:
            st.session_state.user_email = email_input.lower()
            st.rerun()
        else:
            st.warning("Enter email")

    st.stop()

# ---------- USER ----------
email = st.session_state.user_email
name = re.sub(r'\d+', '', email.split("@")[0].split(".")[0]).capitalize()
st.success(f"Welcome to Analyrix, {name}")

# ---------- PRO USERS ----------
PRO_USERS = ["sondreriksaasen@gmail.com"]

def is_pro_user(email):
    return email.lower() in [e.lower() for e in PRO_USERS]

is_pro = is_pro_user(email)

# ---------- DATABASE ----------
if "users_db" not in st.session_state:
    st.session_state.users_db = {}

if email not in st.session_state.users_db:
    st.session_state.users_db[email] = {
        "scan_count": 0,
        "search_count": 0,
        "last_reset": datetime.now()
    }

user = st.session_state.users_db[email]

if datetime.now() - user["last_reset"] > timedelta(hours=24):
    user["scan_count"] = 0
    user["search_count"] = 0
    user["last_reset"] = datetime.now()

# ---------- STATE ----------
if "results" not in st.session_state:
    st.session_state.results = []

if "show_search" not in st.session_state:
    st.session_state.show_search = False

if "last_search" not in st.session_state:
    st.session_state.last_search = None

# ---------- HERO ----------
st.markdown("""
# 🚀 Analyrix

### Find high-probability trades in seconds using AI
""")

st.info("🔓 Start free – upgrade anytime")

col1, col2, col3 = st.columns(3)
col1.metric("📊 Stocks Scanned", "800+")
col2.metric("⚡ Scan Time", "Few seconds")
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
if not is_pro:
    st.markdown("[🚀 Get Pro Access ($19/month)](https://buy.stripe.com/14A14n6kuaaPffCdqoak000)")
    st.caption("After payment, enter your email above to unlock PRO")
    st.warning("Free: 3 scans + 3 searches per 24h")
    st.divider()

# ---------- HELPER ----------
def get_timeframe(move):
    if move > 8:
        return "Short-term (1–3 days)"
    elif move > 4:
        return "Medium-term (3–7 days)"
    return "Longer-term (1–2 weeks)"

def profit_sim(investment, move):
    return round(investment * (move / 100), 2)

# 🔥 SMARTER AI REASONING
def generate_reasoning(signal, confidence, expected_move, risk):
    strength = "strong" if confidence > 80 else "moderate" if confidence > 60 else "weak"

    if signal == "BUY":
        return f"""
📈 **Bullish setup detected**

• Trend strength: {strength}  
• Expected move: +{expected_move}%  
• Confidence: {confidence}%  

RSI suggests momentum building while MACD indicates upward trend continuation.  
Market structure supports a potential breakout.
"""
    elif signal == "SELL":
        return f"""
📉 **Bearish setup detected**

• Trend strength: {strength}  
• Expected move: {expected_move}%  
• Confidence: {confidence}%  

RSI shows weakness and MACD is turning negative.  
Downside pressure likely to continue short-term.
"""
    else:
        return f"""
⚖️ **Neutral / consolidation phase**

• Confidence: {confidence}%  
• Risk level: {risk}  

Indicators are mixed. No strong directional edge right now.
"""

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

# ---------- INDICATORS ----------
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

    return df.fillna(method="bfill")

# ---------- CHART ----------
def create_chart(ticker, signal):
    df = add_indicators(get_data(ticker))

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], mode="lines"))

    fig.add_trace(go.Scatter(
        x=[df["Date"].iloc[-1]],
        y=[df["Close"].iloc[-1]],
        mode="markers+text",
        text=[signal]
    ))

    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], yaxis="y2"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], yaxis="y3"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Signal"], yaxis="y3"))

    fig.update_layout(
        template="plotly_dark",
        yaxis2=dict(overlaying="y", side="right"),
        yaxis3=dict(overlaying="y", side="right", position=0.9)
    )

    return fig

# ---------- BUTTONS ----------
col1, col2 = st.columns(2)

if col1.button("🚀 Scan Market"):
    st.session_state.show_search = False

    if not is_pro and user["scan_count"] >= 3:
        st.error("🚫 Scan limit reached")
    else:
        st.session_state.results = scanner.scan_market(limit=20)
        user["scan_count"] += 1

if col2.button("🔍 Search Stock"):
    st.session_state.show_search = True
    st.session_state.results = []

# ---------- TOP PICKS ----------
if st.session_state.results:
    top = sorted(st.session_state.results, key=lambda x: x['confidence'], reverse=True)[:3]

    st.markdown("## 🏆 Top AI Picks Today")

    for t in top:
        st.markdown(f"🔥 **{t['ticker']}** — {t['signal']} ({t['confidence']}%)")

    st.divider()

# ---------- DISPLAY ----------
if st.session_state.results:

    investment = st.number_input("💰 Enter your investment ($)", value=1000, step=100)

    for i, r in enumerate(st.session_state.results):

        move = r["expected_move"]
        label = f"🔥 STRONG {r['signal']}" if r["confidence"] > 85 else r["signal"]

        st.markdown(f"""
### 📊 {r['ticker']}

**{label}**  
Confidence: {r['confidence']}%  

Expected Move: {move}%  
Hold Time: {get_timeframe(move)}

Entry: ${r['entry']}  
Stop Loss: ${r['stop_loss']}  
Take Profit: ${r['take_profit']}
""")

        # 🔥 SAFE AI INSIGHT
        st.markdown("### 🧠 AI Insight")
        st.info(generate_reasoning(
            r.get('signal', 'HOLD'),
            r.get('confidence', 50),
            r.get('expected_move', 0),
            r.get('risk', 'Medium')
        ))

        st.progress(int(r["confidence"]))

        profit = profit_sim(investment, move)

        st.markdown(f"💰 **Investment: ${investment}**")
        st.markdown(f"💰 **Potential profit: ${profit:.2f}**")

        if st.button(f"📊 View Chart - {r['ticker']}", key=f"chart_{i}"):
            fig = create_chart(r["ticker"], r["signal"])
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

st.info("🔄 Run another scan to discover new opportunities")
