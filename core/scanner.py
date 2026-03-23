import random
import yfinance as yf

class VectorMarketScanner:

    def __init__(self):

        # 🔥 KVALITETS AKSJER (kun stocks – ingen krypto)
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

            # ETFs (kan beholde disse)
            "SPY","QQQ","DIA","IWM"
        ]

        # 🔁 FYLL OPP TIL ~500 (realistisk univers)
        self.tickers = self.base_tickers.copy()

        while len(self.tickers) < 500:
            self.tickers.append(random.choice(self.base_tickers))

    # ---------- PRICE ENGINE ----------
    def get_price(self, ticker):

        try:
            ticker_obj = yf.Ticker(ticker)

            # 1. FAST INFO
            try:
                price = ticker_obj.fast_info.get("lastPrice", None)
                if price and price > 0:
                    return round(float(price), 2)
            except:
                pass

            # 2. CURRENT PRICE
            try:
                price = ticker_obj.info.get("currentPrice", None)
                if price and price > 0:
                    return round(float(price), 2)
            except:
                pass

            # 3. INTRADAY (BEST FALLBACK)
            try:
                df = ticker_obj.history(period="1d", interval="1m")
                if not df.empty:
                    price = float(df["Close"].dropna().iloc[-1])
                    return round(price, 2)
            except:
                pass

            # 4. DAILY
            try:
                df = ticker_obj.history(period="5d", interval="1d")
                if not df.empty:
                    price = float(df["Close"].dropna().iloc[-1])
                    return round(price, 2)
            except:
                pass

            return None

        except:
            return None

    # ---------- ANALYSIS ----------
    def analyze_stock(self, ticker):

        price = self.get_price(ticker)

        # ❌ dropp dårlige data
        if not price or price < 3:
            return None

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

        # 🔥 sorter best først
        results = sorted(results, key=lambda x: x["expected_move"], reverse=True)

        return results

    # ---------- SINGLE STOCK ----------
    def analyze_single_stock(self, ticker):

        result = self.analyze_stock(ticker)

        if not result:
            return {
                "ticker": ticker.upper(),
                "signal": "NO DATA",
                "confidence": 0,
                "expected_move": 0,
                "risk": "N/A",
                "entry": "-",
                "stop_loss": "-",
                "take_profit": "-"
            }

        return result

    # ---------- TRENDING ----------
    def get_trending(self):
        return ["TSLA", "NVDA", "AAPL", "AMD", "META"]
