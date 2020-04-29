from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QHBoxLayout, QLabel
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QPoint
import numpy as np
import pyqtgraph as pg
import sys


class PickBrush(QWidget):
    def __init__(self):
        super(PickBrush, self).__init__()
        self.layout = QHBoxLayout(self)
        self.img = QPixmap(400, 400)
        self.img.fill(Qt.black)
        self.label = QLabel()
        self.label.setPixmap(self.img)
        self.layout.addWidget(self.label)

        self.painting = False
        self.brushSize = 5
        self.brushColor = Qt.darkCyan
        self.lastPoint = QPoint()

    def mousePressEvent(self, a0):
        super(PickBrush, self).mousePressEvent(a0)
        if a0.button() == Qt.LeftButton:
            self.painting = True
            self.lastPoint = a0.pos()

    def mouseReleaseEvent(self, a0):
        super(PickBrush, self).mouseReleaseEvent(a0)
        if a0.button() == Qt.LeftButton:
            self.painting = False

    def mouseMoveEvent(self, a0):
        if (a0.buttons() & Qt.LeftButton) & self.painting:
            painter = QPainter(self.img)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, a0.pos())
            painter.end()
            self.lastPoint = a0.pos()
            self.label.setPixmap(self.img)
            print(a0.pos())

    def paintEvent(self, event):
        super(PickBrush, self).paintEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PickBrush()
    window.show()
    app.exec()
