from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
import numpy as np
import pyqtgraph as pg
import sys
import os

dot = np.array([[1]]).astype(np.int8)
eraser = np.array([[-1]]).astype(np.int8)
current_directory = os.path.dirname(os.path.realpath(__file__))


class BonusBrush(QWidget):
    def __init__(self):
        super(BonusBrush, self).__init__()
        self.setWindowTitle("Design New Brush")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout = QVBoxLayout(self)

        self.kernel = dot
        self.g_item = pg.GraphicsView()
        self.vbox = pg.ViewBox()
        self.pen = np.zeros((5, 5)).astype(np.int8)
        self.img = pg.ImageItem(self.pen, autoDownSmaple=False)
        self.img.setLevels([-1, 1])
        self.img.setDrawKernel(self.kernel, mask=self.kernel, center=(0, 0), mode='add')

        self.vbox.addItem(self.img)
        self.vbox.setMouseEnabled(x=False, y=False)
        self.g_item.setCentralItem(self.vbox)
        self.layout.addWidget(self.g_item)

        self.hlayout = QHBoxLayout()
        self.label = QLabel("Size")
        self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.hlayout.addWidget(self.label)
        self.pen_size = QLineEdit("5")
        int_ensurer = QtGui.QIntValidator(1, 500)
        self.pen_size.setValidator(int_ensurer)
        self.pen_size.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.pen_size.textChanged.connect(self.new_matrix_size)
        self.hlayout.addWidget(self.pen_size)

        self.buttn = QPushButton("DONE")
        self.buttn.clicked.connect(self.disappear)
        self.buttn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.hlayout.addWidget(self.buttn)

        self.pen_button = QPushButton()
        self.pen_button.setIcon(QIcon(os.path.join(current_directory, "images/pen.png")))
        self.pen_button.setIconSize(QSize(30, 30))

        self.rub_button = QPushButton()
        self.rub_button.setIcon(QIcon(os.path.join(current_directory, "images/eraser.png")))
        self.rub_button.setIconSize(QSize(30, 30))

        self.pen_button.clicked.connect(self.set_pen)
        self.rub_button.clicked.connect(self.set_rub)
        self.hlayout.addWidget(self.pen_button)
        self.hlayout.addWidget(self.rub_button)

        self.layout.addLayout(self.hlayout)

    def new_matrix_size(self):
        txt = self.pen_size.text()
        val = 1 if (len(txt) == 0) or (int(txt) == 0) else int(txt)
        self.pen.resize((val, val), refcheck=False)
        self.img.setImage(self.pen)
        self.img.setLevels([-1, 1])

    def disappear(self):
        self.setVisible(False)
        self.pen = np.clip(self.pen, -1, 1)
        self.img.setImage(self.pen)
        self.img.setLevels([-1, 1])

    def change_kernel(self, new_kernel):
        self.kernel = new_kernel
        center = len(self.kernel) // 2
        self.img.setDrawKernel(self.kernel, mask=self.kernel, center=(center, center), mode='add')

    def set_pen(self):
        self.change_kernel(dot)

    def set_rub(self):
        self.change_kernel(eraser)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BonusBrush()
    window.show()
    app.exec()
