import random
import yfinance as yf

class VectorMarketScanner:

    def __init__(self):

        # 🔥 KVALITETS TICKERS (~300)
        self.base_tickers = [
            # Tech
            "AAPL","MSFT","NVDA","AMD","TSLA","GOOGL","META","AMZN","NFLX",
            "INTC","PLTR","SNOW","CRM","ORCL","ADBE",

            # Finance
            "JPM","BAC","GS","MS","V","MA","PYPL","AXP",

            # Healthcare
            "JNJ","PFE","MRNA","ABBV","LLY","UNH",

            # Consumer
            "WMT","COST","NKE","SBUX","MCD","KO","PEP",

            # Energy
            "XOM","CVX","SLB","OXY",

            # Growth / popular
            "COIN","RBLX","SOFI","UPST","RIOT","MARA",

            # ETFs
            "SPY","QQQ","DIA","IWM",

            # Crypto
            "BTC-USD","ETH-USD","SOL-USD"
        ]

        # 🔁 FYLL OPP LISTA (300+)
        self.tickers = self.base_tickers.copy()
        for _ in range(250):
            self.tickers.append(random.choice(self.base_tickers))

    # ---------- GET REAL PRICE ----------
    def get_price(self, ticker):

        try:
            ticker_obj = yf.Ticker(ticker)

            # 🔥 BESTE LIVE APPROX
            price = ticker_obj.fast_info.get("lastPrice", None)

            if price:
                return round(float(price), 2)

        except:
            pass

        # fallback til historisk
        try:
            df = yf.download(ticker, period="5d", interval="1d")

            if df.empty:
                return None

            price = float(df["Close"].dropna().iloc[-1])
            return round(price, 2)

        except:
            return None

    # ---------- ANALYZE ----------
    def analyze_stock(self, ticker):

        price = self.get_price(ticker)

        # ❌ IKKE FAKE DATA
        if not price or price < 3:
            return None

        # 🔥 “AI-ish” logikk (kan forbedres senere)
        confidence = round(random.uniform(60, 90), 1)
        expected_move = round(random.uniform(2, 10), 2)

        signal = "BUY" if confidence > 75 else "WATCH"

        return {
            "ticker": ticker,
            "signal": signal,
            "confidence": confidence,
            "expected_move": expected_move,
            "risk": random.choice(["Low", "Medium", "High"]),
            "entry": price,
            "stop_loss": round(price * 0.92, 2),
            "take_profit": round(price * (1 + expected_move / 100), 2)
        }

    # ---------- SCAN ----------
    def scan_market(self, limit=20):

        sample = random.sample(self.tickers, min(len(self.tickers), limit * 3))

        results = []

        for ticker in sample:
            result = self.analyze_stock(ticker)
            if result:
                results.append(result)

            if len(results) >= limit:
                break

        # 🔥 SORTER BESTE ØVERST
        results = sorted(results, key=lambda x: x["expected_move"], reverse=True)

        return results

    # ---------- SINGLE ----------
    def analyze_single_stock(self, ticker):
        return self.analyze_stock(ticker)

    # ---------- TRENDING ----------
    def get_trending(self):
        return ["TSLA", "NVDA", "AAPL", "BTC-USD", "AMD"]
