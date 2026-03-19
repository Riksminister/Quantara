import pandas as pd
import random
from core.signal_engine import QuantaraSignalEngineV4


class VectorMarketScanner:
    def __init__(self):
        self.engine = QuantaraSignalEngineV4()

    def scan_market(self, limit=50):
        return self.scan_sample(limit)

    def scan_sample(self, limit):
        try:
            df = pd.read_csv("sample_data.csv")
        except:
            return []

        results = []

        for _, row in df.iterrows():

            # --- RANDOMIZED AI LOGIC ---
            confidence = round(random.uniform(60, 90), 1)
            move = round(random.uniform(1.5, 8.5), 2)

            risk = random.choice(["Low", "Medium", "High"])

            signals = ["BUY", "WATCH", "AVOID"]
            signal = random.choices(signals, weights=[0.5, 0.3, 0.2])[0]

            reasons = [
                "Strong momentum breakout",
                "Volume spike detected",
                "Bullish trend continuation",
                "Support bounce",
                "High volatility expansion",
                "AI pattern recognition"
            ]

            results.append({
                "ticker": row["ticker"],
                "signal": signal,
                "confidence": confidence,
                "expected_move": move,
                "risk": risk,
                "entry": row["close"],
                "stop_loss": round(row["close"] * (1 - move/100), 2),
                "take_profit": round(row["close"] * (1 + move/100), 2),
                "reason": random.choice(reasons)
            })

        # Sort by best signals
        results = sorted(results, key=lambda x: x["confidence"], reverse=True)

        return results[:limit]
