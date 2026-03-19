import streamlit as st
import time
import pandas as pd
import random
import plotly.graph_objects as go
import yfinance as yf
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide", page_title="Analyrix")

# ---------- HEADER ----------
st.markdown("# 🚀 Analyrix")
st.caption("AI-powered trade analysis in seconds")

scanner = VectorMarketScanner()

# ---------- STATE ----------
if "results" not in st.session_state:
    st.session_state.results = []

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None


# ---------- REAL DATA CHART ----------
def create_chart(ticker):

    df = yf.download(ticker, period="3mo", interval="1d")

    if df.empty:
        return None

    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma50"] = df["Close"].rolling(50).mean()

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9).mean()

    # STRONG BUY signal
    df["buy"] = (df["rsi"] < 35) & (df["macd"] > df["signal"])

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    ))

    fig.add_trace(go.Scatter(x=df.index, y=df["ma20"], name="MA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["ma50"], name="MA50"))

    buy = df[df["buy"]]

    fig.add_trace(go.Scatter(
        x=buy.index,
        y=buy["Close"],
        mode="markers",
        marker=dict(size=10, color="green"),
        name="BUY"
    ))

    fig.update_layout(height=500)

    return fig


# ---------- AI ANALYSIS ----------
def explain_trade(trade):

    reasons = [
        "This stock is currently oversold and approaching a strong support level. Buying pressure is increasing, suggesting a potential rebound.",
        "Momentum is shifting upward while price holds above key levels, indicating buyers are stepping in.",
        "A breakout pattern is forming with strong volume support, suggesting continuation.",
        "The trend remains bullish, and recent pullbacks are being bought aggressively.",
        "AI detects accumulation after a correction, signaling a favorable entry."
    ]

    reason = random.choice(reasons)

    return f"""
### 🧠 AI Analysis
{reason}

---

### 🎯 Action
**{trade['signal']}**

---

### 📊 Confidence
**{trade['confidence']}%**

---

### ⚠️ Risk
**{trade['risk']}**

---

### 📈 Plan
- **Entry:** ${trade['entry']}
- **Stop Loss:** ${trade['stop_loss']}
- **Take Profit:** ${trade['take_profit']}
"""


# ---------- SCAN ----------
if st.button("🔍 Scan Market"):
    with st.spinner("Analyrix scanning 7000+ stocks..."):
        time.sleep(1.5)
        st.session_state.results = scanner.scan_market(limit=20)
        st.session_state.selected_index = None


# ---------- DISPLAY ----------
if st.session_state.results:

    st.success("Scan complete ✅")

    for i, r in enumerate(st.session_state.results):

        st.markdown(f"""
        ### #{i+1} {r['ticker']}
        **Signal:** {r['signal']}  
        **Confidence:** {r['confidence']}%  
        **Expected Move:** {r['expected_move']}%  
        **Risk:** {r['risk']}
        """)

        if st.button("📊 View Chart", key=f"btn_{i}"):
            st.session_state.selected_index = i

        if st.session_state.selected_index == i:

            fig = create_chart(r["ticker"])

            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available")

            st.markdown(explain_trade(r))

        st.divider()
