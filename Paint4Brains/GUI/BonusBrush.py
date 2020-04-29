from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import numpy as np
import pyqtgraph as pg
import sys

dot = np.array([[1]]).astype(np.int8)
rubber = np.array([[-1]]).astype(np.int8)


class BonusBrush(QWidget):
    def __init__(self):
        super(BonusBrush, self).__init__()
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.layout = QVBoxLayout(self)

        self.g_item = pg.GraphicsView()
        self.vbox = pg.ViewBox()
        self.pen = np.zeros((10, 10)).astype(np.int8)
        self.img = pg.ImageItem(self.pen, autoDownSmaple=False)
        self.img.setLevels([-1, 1])
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
        int_ensurer = QtGui.QIntValidator(1, 500)
        self.pen_size.setValidator(int_ensurer)
        self.pen_size.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.pen_size.textChanged.connect(self.new_matrix_size)
        self.hlayout.addWidget(self.pen_size)

        self.buttn = QPushButton("DONE")
        self.buttn.clicked.connect(self.disappear)
        self.buttn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.hlayout.addWidget(self.buttn)

        self.layout.addLayout(self.hlayout)

    def new_matrix_size(self):
        txt = self.pen_size.text()
        val = 1 if (len(txt) == 0) or (int(txt) == 0) else int(txt)
        self.pen.resize((val, val), refcheck= False)
        self.img.setImage(self.pen)
        self.img.setLevels([-1, 1])

    def disappear(self):
        self.setVisible(False)
        self.pen = np.clip(self.pen, -1, 1)

    def appear(self):
        self.setVisible(True)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BonusBrush()
    window.show()
    app.exec()
