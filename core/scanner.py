import duckdb
import pandas as pd
import numpy as np


class VectorMarketScanner:

    def __init__(self):
        self.conn = duckdb.connect("data/market_data.db", read_only=True)

    # ---------- GET ALL TICKERS ----------
    def get_all_tickers(self):
        query = "SELECT DISTINCT ticker FROM prices"
        result = self.conn.execute(query).fetchall()
        return [r[0] for r in result]

    # ---------- GET DATA ----------
    def get_data(self, ticker):
        query = f"""
        SELECT * FROM prices
        WHERE ticker = '{ticker}'
        ORDER BY date
        """
        df = self.conn.execute(query).fetchdf()
        return df

    # ---------- ANALYZE ----------
    def analyze(self, df):

        # 🔥 tillat flere aksjer
        if len(df) < 20:
            return None

        close = df["close"]

        # Moving averages
        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()

        # Momentum (5 dager)
        momentum = close.iloc[-1] / close.iloc[-5] - 1

        # Volatility
        volatility = close.pct_change().std()

        # ---------- SIGNAL ----------
        signal = "WATCH"
        confidence = 60

        if ma20.iloc[-1] > ma50.iloc[-1] and momentum > 0:
            signal = "BUY"
            confidence += 20

        if momentum < -0.03:
            signal = "AVOID"
            confidence -= 10

        # ---------- RISK ----------
        if volatility > 0.04:
            risk = "High"
        elif volatility > 0.02:
            risk = "Medium"
        else:
            risk = "Low"

        # ---------- EXPECTED MOVE ----------
        expected_move = round(volatility * 100 * 1.5, 2)

        # ---------- PRICE LEVELS (FIXED) ----------
        entry = round(close.iloc[-1], 2)

        # 🔥 MER REALISTISK (IKKE FOR STORE SL)
        stop_loss = round(entry * 0.97, 2)   # -3%
        take_profit = round(entry * 1.06, 2) # +6%

        return {
            "signal": signal,
            "confidence": round(confidence, 1),
            "expected_move": expected_move,
            "risk": risk,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit
        }

    # ---------- SCAN ----------
    def scan_market(self, limit=20):

        tickers = self.get_all_tickers()

        results = []

        for ticker in tickers:

            try:
                df = self.get_data(ticker)
                analysis = self.analyze(df)

                if analysis:
                    analysis["ticker"] = ticker
                    results.append(analysis)

            except:
                continue

        # 🔥 SORT BEST FIRST
        results = sorted(
            results,
            key=lambda x: x["expected_move"],
            reverse=True
        )

        return results[:limit]
