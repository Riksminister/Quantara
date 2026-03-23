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

# ---------- LOGIN ----------
if "user_email" not in st.session_state:
    st.session_state.user_email = None

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

# ---------- PRO ----------
PRO_USERS = ["sondreriksaasen@gmail.com"]

def is_pro_user(email):
    return email.lower() in PRO_USERS

is_pro = is_pro_user(email)

# ---------- USER DB ----------
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

# ---------- HEADER ----------
st.markdown("# 🚀 Analyrix")
st.info("🔓 Start free – upgrade anytime")

col1, col2 = st.columns(2)

scanner = VectorMarketScanner()

# ---------- PAYWALL ----------
if not is_pro:
    st.markdown("[🚀 Get Pro Access ($19/month)](https://buy.stripe.com/14A14n6kuaaPffCdqoak000)")
    st.warning("Free: 3 scans + 3 searches per day")

# ---------- REASON ----------
def generate_reasoning(signal, confidence, expected_move, risk):
    if signal == "BUY":
        return f"Bullish momentum detected with {confidence}% confidence."
    elif signal == "SELL":
        return f"Bearish pressure detected with {confidence}% confidence."
    return f"Mixed signals. Risk level: {risk}."

# ---------- DATA ----------
def get_data(ticker):
    df = yf.download(ticker, period="3mo", progress=False)
    df = df.reset_index()
    return df

# ---------- INDICATORS ----------
def add_indicators(df):
    df["RSI"] = 50
    df["MACD"] = 0
    df["Signal"] = 0
    return df

# ---------- CHART ----------
def create_chart(ticker, signal):
    df = get_data(ticker)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], mode="lines"))

    fig.add_trace(go.Scatter(
        x=[df["Date"].iloc[-1]],
        y=[df["Close"].iloc[-1]],
        mode="markers+text",
        text=[signal]
    ))

    return fig

# ---------- BUTTONS ----------
if col1.button("🚀 Scan Market"):
    st.session_state.show_search = False

    if not is_pro and user["scan_count"] >= 3:
        st.error("Limit reached")
    else:
        results = scanner.scan_market(limit=20)
        st.session_state.results = results
        user["scan_count"] += 1

if col2.button("🔍 Search Stock"):
    st.session_state.show_search = True
    st.session_state.results = []

# ---------- SEARCH ----------
if st.session_state.show_search:
    ticker = st.text_input("Enter ticker")

    if ticker:
        result = scanner.analyze_single_stock(ticker.upper())

        if result:
            st.markdown(f"## {result['ticker']}")

            st.markdown(f"Signal: {result['signal']}")
            st.progress(int(result["confidence"]))

            st.markdown(f"""
Entry: ${result['entry']}  
Stop Loss: ${result['stop_loss']}  
Take Profit: ${result['take_profit']}
""")

            st.markdown(generate_reasoning(
                result["signal"],
                result["confidence"],
                result["expected_move"],
                result["risk"]
            ))

            st.plotly_chart(create_chart(result["ticker"], result["signal"]))

# ---------- TOP PICKS ----------
if st.session_state.results:

    top = sorted(st.session_state.results, key=lambda x: x['confidence'], reverse=True)[:3]

    st.markdown("## 🏆 Top AI Picks Today")

    for t in top:
        st.markdown(f"**{t['ticker']}** — {t['signal']} ({t['confidence']}%)")

# ---------- DISPLAY ----------
if st.session_state.results:

    for i, r in enumerate(st.session_state.results):

        label = f"🔥 STRONG {r['signal']}" if r["confidence"] > 85 else r["signal"]

        st.markdown(f"""
### 📊 {r['ticker']}

**{label}**  
Confidence: {r['confidence']}%  
Expected Move: {r['expected_move']}%  
Risk: {r['risk']}
""")

        st.progress(int(r["confidence"]))

        st.markdown(f"""
Entry: ${r['entry']}  
Stop Loss: ${r['stop_loss']}  
Take Profit: ${r['take_profit']}
""")

        st.markdown(generate_reasoning(
            r["signal"],
            r["confidence"],
            r["expected_move"],
            r["risk"]
        ))

        if st.button(f"Chart {r['ticker']}", key=i):
            st.plotly_chart(create_chart(r["ticker"], r["signal"]))

        st.divider()

st.info("🔄 Run another scan to discover new opportunities")
