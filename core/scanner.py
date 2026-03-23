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

    st.markdown("## 🔐 Get started")

    email_input = st.text_input("Enter your email")

    if st.button("Continue"):
        if email_input:
            st.session_state.user_email = email_input.lower()
            st.rerun()
        else:
            st.warning("Enter email")

    st.stop()

email = st.session_state.user_email
name = re.sub(r'\d+', '', email.split("@")[0].split(".")[0]).capitalize()
st.success(f"Welcome to Analyrix, {name}")

# ---------- PRO ----------
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

# ---------- HEADER ----------
st.markdown("# 🚀 Analyrix")
st.info("🔓 Start free – upgrade anytime")

col1, col2 = st.columns(2)

# ---------- SCAN ----------
if col1.button("🚀 Scan Market"):

    st.session_state.show_search = False

    if not is_pro and user["scan_count"] >= 3:
        st.error("🚫 Scan limit reached")
    else:
        with st.spinner("Scanning 800+ stocks using AI..."):
            st.session_state.results = VectorMarketScanner().scan_market(limit=20)
            user["scan_count"] += 1

# ---------- SEARCH ----------
if col2.button("🔍 Search Stock"):
    st.session_state.show_search = True
    st.session_state.results = []

# ---------- SEARCH INPUT ----------
if st.session_state.show_search:

    ticker_input = st.text_input("Enter ticker and press ENTER")

    if ticker_input and ticker_input != st.session_state.last_search:

        if not is_pro and user["search_count"] >= 3:
            st.error("🚫 Search limit reached")
        else:
            with st.spinner(f"Analyzing {ticker_input.upper()}..."):

                result = VectorMarketScanner().analyze_single_stock(ticker_input.upper())
                st.session_state.last_search = ticker_input
                user["search_count"] += 1

                if result:
                    st.markdown(f"""
                    ### 📊 {result['ticker']}

                    **🧠 AI Signal:** {result['signal']}  
                    **📊 AI Confidence:** {result['confidence']}%  
                    **📈 Expected Move:** {result['expected_move']}%  
                    **⚠️ Risk Level:** {result['risk']}
                    """)

# ---------- DISPLAY RESULTS (🔥 FIX) ----------
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

            df = yf.download(r["ticker"], period="6mo", interval="1d")

            if not df.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines"))
                st.plotly_chart(fig, use_container_width=True)

        st.divider()
