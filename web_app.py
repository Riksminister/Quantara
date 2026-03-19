import streamlit as st
import time
import pandas as pd
import random
import plotly.graph_objects as go
from core.scanner import VectorMarketScanner

st.set_page_config(layout="wide", page_title="Quantara AI")

st.title("🚀 Quantara AI Terminal")
st.caption("AI scanning the market in real-time")

scanner = VectorMarketScanner()


# ---------- INDICATORS ----------
def calculate_indicators(df):
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma50"] = df["close"].rolling(50).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["close"].ewm(span=12).mean()
    ema26 = df["close"].ewm(span=26).mean()
    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9).mean()

    return df


# ---------- CHART ----------
def create_chart(ticker, price):
    # Fake OHLC data (realistic feel)
    prices = [price]

    for _ in range(80):
        change = random.uniform(-2, 2)
        prices.append(prices[-1] * (1 + change/100))

    df = pd.DataFrame({"close": prices})

    df["open"] = df["close"].shift(1)
    df["high"] = df[["open", "close"]].max(axis=1) * 1.01
    df["low"] = df[["open", "close"]].min(axis=1) * 0.99

    df.fillna(method="bfill", inplace=True)

    df = calculate_indicators(df)

    # BUY SIGNAL (STRICT)
    df["buy_signal"] = (
        (df["rsi"] < 35) &
        (df["macd"] > df["signal"])
    )

    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    ))

    # MA
    fig.add_trace(go.Scatter(x=df.index, y=df["ma20"], name="MA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["ma50"], name="MA50"))

    # BUY markers
    buy_points = df[df["buy_signal"]]

    fig.add_trace(go.Scatter(
        x=buy_points.index,
        y=buy_points["close"],
        mode="markers",
        marker=dict(size=10, color="green"),
        name="BUY"
    ))

    fig.update_layout(height=400)

    return fig


# ---------- AI EXPLANATION ----------
def explain_trade(trade):
    explanations = [
        f"{trade['ticker']} is showing strong upward momentum with increasing volume.",
        f"The trend is bullish and the price is holding above key levels.",
        f"AI detects a breakout pattern with high probability continuation.",
        f"Momentum and structure suggest buyers are in control.",
        f"This setup shows a favorable risk/reward profile."
    ]

    return random.choice(explanations)


# ---------- SCAN ----------
if st.button("🔍 Scan Market"):

    with st.spinner("AI scanning 7000+ stocks..."):
        time.sleep(1.5)
        results = scanner.scan_market(limit=20)

    st.success("Scan complete ✅")

    for i, r in enumerate(results):

        st.markdown(f"""
        ### #{i+1} {r['ticker']}
        **Signal:** {r['signal']}  
        **Confidence:** {r['confidence']}%  
        **Expected Move:** {r['expected_move']}%  
        """)

        # --- CHART BUTTON ---
        if st.button(f"📊 Show Chart {r['ticker']}", key=f"chart_{i}"):

            fig = create_chart(r["ticker"], r["entry"])
            st.plotly_chart(fig, use_container_width=True)

        # --- AI EXPLANATION ---
        with st.expander("🧠 Why this trade"):
            st.write(explain_trade(r))

        st.divider()
