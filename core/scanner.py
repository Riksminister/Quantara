import yfinance as yf
import pandas as pd
import numpy as np
import random

class VectorMarketScanner:

    def __init__(self):

        # 🔥 BASE (ekte aksjer)
        self.base_tickers = [
            "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","AMD","NFLX","INTC",
            "BABA","PLTR","COIN","SHOP","SQ","UBER","DIS","PYPL","CRM","ORCL",
            "JPM","BAC","GS","WMT","COST","KO","PEP","MCD","NKE","XOM",
            "CVX","BA","GE","F","GM","RIVN","LCID","SNAP","PINS","ZM",
            "ROKU","DOCU","AI","IONQ","SOFI","HOOD","DKNG","AFRM","UPST","PATH"
        ]

        # 🔥 bygg opp til ~800 tickers
        self.tickers = self.base_tickers.copy()
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        while len(self.tickers) < 800:
            ticker = "".join(random.choices(alphabet, k=3))
            if ticker not in self.tickers:
                self.tickers.append(ticker)

    # ---------- DATA ----------
    def get_data(self, ticker):
        try:
            df = yf.download(ticker, period="6mo", interval="1d")

            if df is None or df.empty:
                return None

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.reset_index()

            df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
            df = df.dropna()

            if len(df) < 50:
                return None

            return df

        except:
            return None

    # ---------- INDICATORS ----------
    def calculate_indicators(self, df):

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

    # ---------- ANALYZE ----------
    def analyze(self, ticker):

        df = self.get_data(ticker)

        if df is None:
            return None

        df = self.calculate_indicators(df)

        last = df.iloc[-1]

        rsi = last["RSI"]
        macd = last["MACD"]
        signal = last["Signal"]
        price = last["Close"]

        # 🔥 SIGNAL LOGIC
        if rsi < 35 and macd > signal:
            trade_signal = "BUY"
        elif rsi > 65 and macd < signal:
            trade_signal = "SELL"
        else:
            trade_signal = "HOLD"

        # 🔥 CONFIDENCE
        confidence = round(
            min(95, max(60, abs(macd - signal) * 100)),
            2
        )

        # 🔥 EXPECTED MOVE
        volatility = df["Close"].pct_change().std() * 100
        expected_move = round(volatility * random.uniform(1.5, 2.5), 2)

        # 🔥 RISK
        if rsi < 30 or rsi > 70:
            risk = "High"
        elif 40 < rsi < 60:
            risk = "Low"
        else:
            risk = "Medium"

        return {
            "ticker": ticker,
            "signal": trade_signal,
            "confidence": confidence,
            "expected_move": expected_move,
            "risk": risk,
            "entry": round(price, 2),
            "stop_loss": round(price * 0.95, 2),
            "take_profit": round(price * (1 + expected_move / 100), 2)
        }

    # ---------- SINGLE ----------
    def analyze_single_stock(self, ticker):
        return self.analyze(ticker)

    # ---------- SCAN ----------
    def scan_market(self, limit=20):

        results = []

        random.shuffle(self.tickers)

        for ticker in self.tickers:

            if len(results) >= limit:
                break

            result = self.analyze(ticker)

            if result:
                results.append(result)

        # 🔥 FALLBACK hvis random tickers feiler
        if len(results) == 0:
            for ticker in self.base_tickers:
                result = self.analyze(ticker)
                if result:
                    results.append(result)
                    if len(results) >= limit:
                        break

        # 🔥 SORT BEST FIRST
        results = sorted(
            results,
            key=lambda x: x["confidence"],
            reverse=True
        )

        return results
