import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import pandas as pd


class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.generate_picture()

    def generate_picture(self):
        self.picture = pg.QtGui.QPicture()
        p = pg.QtGui.QPainter(self.picture)

        w = 0.4

        for (t, open_, close_, low_, high_) in self.data:
            if close_ >= open_:
                p.setPen(pg.mkPen("green"))
                p.setBrush(pg.mkBrush("green"))
            else:
                p.setPen(pg.mkPen("red"))
                p.setBrush(pg.mkBrush("red"))

            p.drawLine(pg.QtCore.QPointF(t, low_), pg.QtCore.QPointF(t, high_))
            p.drawRect(pg.QtCore.QRectF(t - w, open_, w * 2, close_ - open_))

        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return pg.QtCore.QRectF(self.picture.boundingRect())


class ChartWindow(QWidget):
    def __init__(self, df, ticker):
        super().__init__()

        self.setWindowTitle(ticker)
        self.setGeometry(200, 200, 900, 500)

        layout = QVBoxLayout()
        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)
        self.setLayout(layout)

        self.draw(df)

    def draw(self, df):
        df = df.tail(100).reset_index(drop=True)

        df["ma20"] = df["close"].rolling(20).mean()
        df["ma50"] = df["close"].rolling(50).mean()

        data = []
        for i, row in df.iterrows():
            data.append((i, row["open"], row["close"], row["low"], row["high"]))

        item = CandlestickItem(data)
        self.plot.addItem(item)

        self.plot.plot(df["ma20"], pen=pg.mkPen("cyan"))
        self.plot.plot(df["ma50"], pen=pg.mkPen("yellow"))