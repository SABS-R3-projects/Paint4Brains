from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QHBoxLayout, QLabel
from PyQt5.QtGui import QIcon, QImage, QPainter, QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QPoint
import numpy as np
import pyqtgraph as pg
import sys

dot = np.array([[1]]).astype(np.int8)
rubber = np.array([[-1]]).astype(np.int8)


class PickBrush(QWidget):
    def __init__(self):
        super(PickBrush, self).__init__()
        self.layout = QHBoxLayout(self)

        self.g_item = pg.GraphicsView()
        self.vbox = pg.ViewBox()
        self.pen = np.zeros((20, 20))
        self.img = pg.ImageItem(self.pen, autoDownSmaple=False)
        self.img.setLevels([0, 2])
        self.img.setDrawKernel(dot, mask=dot, center=(0, 0), mode='add')

        self.vbox.addItem(self.img)
        self.vbox.setMouseEnabled(x=False, y=False)
        self.g_item.setCentralItem(self.vbox)
        self.layout.addWidget(self.g_item)

    def mouseDoubleClickEvent(self, a0):
        self.img.setDrawKernel(dot, mask=rubber, center=(0, 0), mode='add')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PickBrush()
    window.show()
    app.exec()
