from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import numpy as np
import pyqtgraph as pg
import sys

dot = np.array([[1]]).astype(np.int8)
rubber = np.array([[-1]]).astype(np.int8)


class PickBrush(QWidget):
    def __init__(self):
        super(PickBrush, self).__init__()
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.layout = QVBoxLayout(self)

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

        self.hlayout = QHBoxLayout()
        self.label = QLabel("Size")
        self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.hlayout.addWidget(self.label)
        self.pen_size = QLineEdit("20")
        self.pen_size.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.pen_size.textChanged.connect(self.new_matrix_size)
        self.hlayout.addWidget(self.pen_size)

        self.buttn = QPushButton("DONE")
        self.buttn.clicked.connect(self.close)
        self.buttn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.hlayout.addWidget(self.buttn)

        self.layout.addLayout(self.hlayout)

    def new_matrix_size(self):
        val = int(self.pen_size.text())
        self.pen = np.zeros((val, val))
        self.img.setImage(self.pen)
        self.img.setLevels([0, 2])






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PickBrush()
    window.show()
    app.exec()
