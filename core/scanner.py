import pandas as pd
from core.signal_engine import QuantaraSignalEngineV4


class VectorMarketScanner:
    def __init__(self, db_path="data/market_data.db"):
        self.conn = duckdb.connect(db_path, read_only=True)
        self.engine = QuantaraSignalEngineV4()

    def get_top_tickers(self, limit=300):
        query = f"""
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
        LIMIT {limit}
        """
        df = self.conn.execute(query).df()
        return df["ticker"].tolist()

    def get_batch_data(self, tickers):
        tickers_str = ",".join([f"'{t}'" for t in tickers])

        query = f"""
        SELECT *
        FROM prices
        WHERE ticker IN ({tickers_str})
        ORDER BY ticker, date
        """
        return self.conn.execute(query).df()

    def scan_market(self, limit=50):
        tickers = self.get_top_tickers(limit=300)

        df = self.get_batch_data(tickers)

        results = []

        # GROUP BY ticker (FAST)
        grouped = df.groupby("ticker")

        for ticker, group in grouped:
            try:
                if len(group) < 60:
                    continue

                signal = self.engine.calculate(group)

                if signal is None:
                    continue

                if signal["signal"] == "BUY":
                    results.append({
                        "ticker": ticker,
                        **signal
                    })

            except:
                continue

        results = sorted(results, key=lambda x: x["confidence"], reverse=True)

        return results[:limit]
