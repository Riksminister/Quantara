import pandas as pd
import os
from core.signal_engine import QuantaraSignalEngineV4


class VectorMarketScanner:
    def __init__(self):
        self.engine = QuantaraSignalEngineV4()

        # Detect if running locally with DB
        self.use_db = os.path.exists("data/market_data.db")

        if self.use_db:
            import duckdb
            self.conn = duckdb.connect("data/market_data.db", read_only=True)
        else:
            self.conn = None

    def scan_market(self, limit=20):
        if self.use_db:
            return self.scan_db(limit)
        else:
            return self.scan_sample()

    # ---------- LOCAL MODE ----------
    def scan_db(self, limit):
        query = """
        SELECT ticker
        FROM (
            SELECT ticker,
                   volume,
                   date,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date DESC) as rn
            FROM prices
        )
        WHERE rn = 1
        ORDER BY volume DESC
        LIMIT 200
        """

        tickers = [row[0] for row in self.conn.execute(query).fetchall()]
        tickers_str = ",".join([f"'{t}'" for t in tickers])

        df = self.conn.execute(f"""
            SELECT *
            FROM prices
            WHERE ticker IN ({tickers_str})
            ORDER BY ticker, date
        """).df()

        results = []

        for ticker, group in df.groupby("ticker"):
            signal = self.engine.calculate(group)

            if signal and signal["signal"] == "BUY":
                results.append({"ticker": ticker, **signal})

        return sorted(results, key=lambda x: x["confidence"], reverse=True)[:limit]

    # ---------- CLOUD MODE ----------
    def scan_sample(self):
        try:
            df = pd.read_csv("data/sample_data.csv")
        except:
            return []

        results = []

        for _, row in df.iterrows():
            results.append({
                "ticker": row["ticker"],
                "signal": "BUY",
                "confidence": 70,
                "expected_move": 3.5,
                "risk": "Medium",
                "entry": row["close"],
                "stop_loss": round(row["close"] * 0.95, 2),
                "take_profit": round(row["close"] * 1.05, 2),
                "reason": "Demo mode (cloud)"
            })

        return results
