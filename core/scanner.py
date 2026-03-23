import yfinance as yf
import pandas as pd
import numpy as np
import random

class VectorMarketScanner:

    def __init__(self):

        # 🔥 STOR LISTE MED EKTE AKSJER (800+ vibe, men stabile)
        self.tickers = [
            "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","AMD","NFLX","INTC",
            "BABA","PLTR","COIN","SHOP","SQ","UBER","DIS","PYPL","CRM","ORCL",
            "JPM","BAC","GS","WMT","COST","KO","PEP","MCD","NKE","XOM",
            "CVX","BA","GE","F","GM","RIVN","LCID","SNAP","PINS","ZM",
            "ROKU","DOCU","AI","IONQ","SOFI","HOOD","DKNG","AFRM","UPST","PATH",

            # 🔥 UTVIDET LISTE
            "ADBE","CSCO","QCOM","TXN","AMAT","INTU","ISRG","MU","LRCX","KLAC",
            "MRVL","SNOW","DDOG","NET","TEAM","CRWD","ZS","OKTA","MDB","PANW",
            "NOW","WDAY","SHOP","SQ","PYPL","MA","V","AXP","BLK","SPGI",

            "ABBV","PFE","MRK","LLY","JNJ","UNH","CVS","TMO","ABT","DHR",
            "BMY","GILD","REGN","VRTX","BIIB",

            "HD","LOW","TGT","WMT","COST","DG","DLTR","BBY","ETSY",

            "XOM","CVX","COP","SLB","EOG","MPC","PSX","VLO",

            "CAT","DE","HON","UPS","FDX","BA","LMT","RTX",

            "TSM","ASML","SONY","SAP","ADSK","ORCL","IBM",

            "SPOT","RBLX","EA","TTWO","U","MTCH",

            "NIO","XPEV","LI","BYDDF",

            "ARKK","QQQ","SPY","IWM"
        ]

    # ---------- DATA ----------
    def get_data(self, ticker):
        try:
            df = yf.download(ticker, period="3mo", interval="1d", progress=False)

            if df is None or df.empty:
                return None

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.reset_index()

            df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
            df = df.dropna()

            if len(df) < 30:
                return None

            return df

        except:
            return None

    # ---------- INDICATORS ----------
    def calculate_indicators(self, df):

        delta = df["Close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        rs = gain.rolling(14).mean() / loss.rolling(14).mean()
        df["RSI"] = 100 - (100 / (1 + rs))

        ema12 = df["Close"].ewm(span=12).mean()
        ema26 = df["Close"].ewm(span=26).mean()

        df["MACD"] = ema12 - ema26
        df["Signal"] = df["MACD"].ewm(span=9).mean()

        return df.fillna(method="bfill")

    # ---------- ANALYZE ----------
    def analyze(self, ticker):

        df = self.get_data(ticker)

        if df is None:
            return None

        df = self.calculate_indicators(df)
        last = df.iloc[-1]

        rsi = last["RSI"]
        macd = last["MACD"]
        signal = last["Signal"]
        price = last["Close"]

        # SIGNAL
        if rsi < 35 and macd > signal:
            trade_signal = "BUY"
        elif rsi > 65 and macd < signal:
            trade_signal = "SELL"
        else:
            trade_signal = "HOLD"

        confidence = round(min(95, max(60, abs(macd - signal) * 100)), 2)

        volatility = df["Close"].pct_change().std() * 100
        expected_move = round(volatility * 2, 2)

        if rsi < 30 or rsi > 70:
            risk = "High"
        elif 40 < rsi < 60:
            risk = "Low"
        else:
            risk = "Medium"

        return {
            "ticker": ticker,
            "signal": trade_signal,
            "confidence": confidence,
            "expected_move": expected_move,
            "risk": risk,
            "entry": round(price, 2),
            "stop_loss": round(price * 0.95, 2),
            "take_profit": round(price * (1 + expected_move / 100), 2)
        }

    # ---------- SINGLE ----------
    def analyze_single_stock(self, ticker):
        return self.analyze(ticker)

    # ---------- SCAN ----------
    def scan_market(self, limit=20):

        results = []

        # 🔥 SCAN KUN ET UTVALG (rask + stabil)
        sample = random.sample(self.tickers, min(len(self.tickers), 100))

        for ticker in sample:

            if len(results) >= limit:
                break

            result = self.analyze(ticker)

            if result:
                results.append(result)

        # 🔥 FALLBACK (GARANTERT RESULTATER)
        if len(results) < limit:
            for ticker in self.tickers:
                result = self.analyze(ticker)
                if result:
                    results.append(result)
                    if len(results) >= limit:
                        break

        return sorted(results, key=lambda x: x["confidence"], reverse=True)
