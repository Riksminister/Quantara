import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QFrame, QPushButton, QScrollArea,
    QLineEdit
)

from core.scanner import VectorMarketScanner
from gui.theme import DARK_THEME
from gui.chart_window import ChartWindow


class TradeCard(QFrame):
    def __init__(self, trade, click_callback):
        super().__init__()

        self.trade = trade
        self.click_callback = click_callback

        self.setObjectName("card")

        layout = QHBoxLayout()

        ticker = QLabel(trade["ticker"])
        ticker.setStyleSheet("font-size: 16px; font-weight: bold;")

        info = QLabel(
            f"{trade['signal']} | {trade['confidence']}% | "
            f"{trade['expected_move']}% | {trade['risk']}"
        )

        layout.addWidget(ticker)
        layout.addStretch()
        layout.addWidget(info)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.click_callback(self.trade)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quantara Terminal")
        self.setGeometry(100, 100, 1100, 800)

        self.scanner = VectorMarketScanner()

        self.start_balance = 1000
        self.current_balance = 1000

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- TOP BAR ---
        top = QHBoxLayout()

        self.balance = QLabel("Balance: $1000")
        self.profit = QLabel("Profit: $0 (0%)")
        self.market = QLabel("Market: Loading...")

        self.balance.setStyleSheet("font-size:18px;font-weight:bold;")

        top.addWidget(self.balance)
        top.addWidget(self.profit)
        top.addStretch()
        top.addWidget(self.market)

        layout.addLayout(top)

        # --- PROFIT INPUT ---
        p_layout = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Today's profit")

        btn = QPushButton("Add")
        btn.clicked.connect(self.add_profit)

        p_layout.addWidget(self.input)
        p_layout.addWidget(btn)

        layout.addLayout(p_layout)

        # --- TITLE ---
        title = QLabel("AI Trade Opportunities")
        title.setStyleSheet("font-size:22px;font-weight:bold;")
        layout.addWidget(title)

        # --- SCROLL ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.scroll_layout = QVBoxLayout()

        self.container.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.container)

        layout.addWidget(self.scroll)

        # --- EXPLANATION ---
        self.explain = QLabel("Select a trade")
        layout.addWidget(self.explain)

        # --- BUTTON ---
        scan = QPushButton("Scan Market")
        scan.clicked.connect(self.load_data)
        layout.addWidget(scan)

        self.setLayout(layout)

    def add_profit(self):
        try:
            val = float(self.input.text())
            self.current_balance += val

            total = self.current_balance - self.start_balance
            pct = (total / self.start_balance) * 100

            self.balance.setText(f"Balance: ${round(self.current_balance,2)}")
            self.profit.setText(f"Profit: ${round(total,2)} ({round(pct,2)}%)")

            self.input.clear()
        except:
            pass

    def load_data(self):
        self.clear()

        trades = self.scanner.scan_market(limit=20)

        self.update_market(trades)

        for t in trades:
            self.scroll_layout.addWidget(TradeCard(t, self.open_trade))

    def open_trade(self, trade):
        df = self.scanner.get_batch_data([trade["ticker"]])

        self.chart = ChartWindow(df, trade["ticker"])
        self.chart.show()

        self.explain.setText(
            f"{trade['ticker']} | {trade['signal']}\n"
            f"Conf: {trade['confidence']}%\n"
            f"Move: {trade['expected_move']}%\n"
            f"Entry: {trade['entry']}"
        )

    def update_market(self, trades):
        if not trades:
            self.market.setText("Market: Unknown")
            return

        avg = sum(t["confidence"] for t in trades) / len(trades)

        if avg > 75:
            state = "Bullish"
        elif avg < 60:
            state = "Bearish"
        else:
            state = "Neutral"

        self.market.setText(f"Market: {state} ({round(avg,1)}%)")

    def clear(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())