import numpy as np
import random


class QuantaraSignalEngineV4:
    def calculate(self, df):
        try:
            if df is None or len(df) < 60:
                return None

            close = df["close"]
            volume = df["volume"]

            ma20 = close.rolling(20).mean()
            ma50 = close.rolling(50).mean()

            momentum = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]
            trend = ma20.iloc[-1] > ma50.iloc[-1]

            volatility = close.pct_change().rolling(20).std().iloc[-1]

            score = 0
            reasons = []

            if momentum > 0.03:
                score += 2
                reasons.append("Strong momentum")
            elif momentum > 0:
                score += 1
                reasons.append("Positive momentum")

            if trend:
                score += 2
                reasons.append("Uptrend (MA20 > MA50)")
            else:
                reasons.append("Weak trend")

            if volatility < 0.03:
                reasons.append("Stable price action")
            else:
                reasons.append("High volatility")

            if score >= 4:
                signal = "BUY"
            elif score >= 2:
                signal = "WATCH"
            else:
                signal = "AVOID"

            confidence = max(45, min(88, 50 + score * 6 + random.uniform(-3, 3)))

            price = close.iloc[-1]

            return {
                "signal": signal,
                "confidence": round(confidence, 1),
                "expected_move": round(volatility * 200, 2),
                "risk": "Low" if volatility < 0.02 else "Medium" if volatility < 0.04 else "High",
                "entry": round(price, 2),
                "stop_loss": round(price * (1 - volatility * 1.5), 2),
                "take_profit": round(price * (1 + volatility * 2.5), 2),
                "reason": ", ".join(reasons)
            }

        except:
            return None