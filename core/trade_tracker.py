import json
import os


class TradeTracker:
    def __init__(self, file="data/trades.json"):
        self.file = file

        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump([], f)

    def add_trade(self, trade):
        trades = self.load()
        trades.append(trade)

        with open(self.file, "w") as f:
            json.dump(trades, f, indent=2)

    def load(self):
        with open(self.file, "r") as f:
            return json.load(f)

    def stats(self):
        trades = self.load()

        wins = sum(1 for t in trades if t.get("result") == "win")
        losses = sum(1 for t in trades if t.get("result") == "loss")

        total = len(trades)

        winrate = (wins / total * 100) if total > 0 else 0

        return {
            "total": total,
            "wins": wins,
            "losses": losses,
            "winrate": round(winrate, 2)
        }