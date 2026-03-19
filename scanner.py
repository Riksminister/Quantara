import pandas as pd
from core.signal_engine import QuantaraSignalEngineV4


class VectorMarketScanner:
    def __init__(self):
        self.engine = QuantaraSignalEngineV4()

    def scan_market(self, limit=20):
        return self.scan_sample(limit)

    def scan_sample(self, limit):
        try:
            df = pd.read_csv("sample_data.csv")
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

        return results[:limit]
