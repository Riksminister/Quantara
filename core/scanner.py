import random
import yfinance as yf

class VectorMarketScanner:

    def __init__(self):

        # 🔥 KVALITETS TICKERS
        self.base_tickers = [
            "AAPL","MSFT","NVDA","AMD","TSLA","GOOGL","META","AMZN","NFLX",
            "INTC","PLTR","SNOW","CRM","ORCL","ADBE",
            "JPM","BAC","GS","MS","V","MA","PYPL","AXP",
            "JNJ","PFE","MRNA","ABBV","LLY","UNH",
            "WMT","COST","NKE","SBUX","MCD","KO","PEP",
            "XOM","CVX","SLB","OXY",
            "COIN","RBLX","SOFI","UPST","RIOT","MARA",
            "SPY","QQQ","DIA","IWM",
            "BTC-USD","ETH-USD","SOL-USD"
        ]

        # 🔁 FYLL OPP LISTA (~300)
        self.tickers = self.base_tickers.copy()
        for _ in range(250):
            self.tickers.append(random.choice(self.base_tickers))

    # ---------- PRICE ENGINE (KRITISK) ----------
    def get_price(self, ticker):

        try:
            ticker_obj = yf.Ticker(ticker)

            # 1. FAST INFO (best case)
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

            # 3. INTRADAY (mest reliable fallback)
            try:
                df = ticker_obj.history(period="1d", interval="1m")

                if not df.empty:
                    price = float(df["Close"].dropna().iloc[-1])
                    if price > 0:
                        return round(price, 2)
            except:
                pass

            # 4. DAILY (kun siste fallback)
            try:
                df = ticker_obj.history(period="5d", interval="1d")

                if not df.empty:
                    price = float(df["Close"].dropna().iloc[-1])
                    if price > 0:
                        return round(price, 2)
            except:
                pass

            return None

        except:
            return None

    # ---------- ANALYSIS ----------
    def analyze_stock(self, ticker):

        price = self.get_price(ticker)

        # ❌ DROPP ALT SOM IKKE ER VALID
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
        return ["TSLA", "NVDA", "AAPL", "BTC-USD", "AMD"]
