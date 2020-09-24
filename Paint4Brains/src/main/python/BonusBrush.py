"""Bonus Brush Module

This file contains a widget class that allows the user to design their own brush.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.BonusBrush import BonusBrush
        brush = BonusBrush()

    It then has to be made visible using:

        brush.setVisible(True)

"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
import numpy as np
import pyqtgraph as pg
import sys
import os
from fbs_runtime.application_context.PyQt5 import ApplicationContext

app = ApplicationContext()

dot = np.array([[1]]).astype(np.int8)
eraser = np.array([[-1]]).astype(np.int8)
current_directory = os.path.dirname(os.path.realpath(__file__))


class BonusBrush(QWidget):

    """BonusBrush class for Paint4Brains.

    This class contains the implementation of a series of methods that allow the user to design a brush.
    """

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
        self.pen_button.setIcon(QIcon(app.get_resource("images/pen.png")))
        self.pen_button.setIconSize(QSize(30, 30))

        self.rub_button = QPushButton()
        self.rub_button.setIcon(QIcon(app.get_resource("images/eraser.png")))
        self.rub_button.setIconSize(QSize(30, 30))

        self.pen_button.clicked.connect(self.set_pen)
        self.rub_button.clicked.connect(self.set_rub)
        self.hlayout.addWidget(self.pen_button)
        self.hlayout.addWidget(self.rub_button)

        self.layout.addLayout(self.hlayout)

    def new_matrix_size(self):
        """ Allows the user to change the size of the new brush

        Depending on the new value in the text box (n), the kernel size is set to nxn
        """
        txt = self.pen_size.text()
        val = 1 if (len(txt) == 0) or (int(txt) == 0) else int(txt)
        self.pen = np.zeros(resize((val, val), refcheck=False)
        self.img.setImage(self.pen)
        self.img.setLevels([-1, 1])

    def disappear(self):
        """ Makes the bonus_brush designing window invisible.

        Some checks are made to ensure that the new brush is within the expected values.
        """
        self.setVisible(False)
        self.pen = np.clip(self.pen, -1, 1)
        self.img.setImage(self.pen)
        self.img.setLevels([-1, 1])

    def change_kernel(self, new_kernel):
        """ Changes the kernel being used to design the bonus brush

        This is basically a helper function to switch between erasing and drawing.
        """
        self.kernel = new_kernel
        center = len(self.kernel) // 2
        self.img.setDrawKernel(self.kernel, mask=self.kernel, center=(center, center), mode='add')

    def set_pen(self):
        """ Set the kernel being used to design the bonus brush to a pen (positive pixel)
        """
        self.change_kernel(dot)

    def set_rub(self):
        """ Set the kernel being used to design the bonus brush to a rubber (negative pixel)
        """
        self.change_kernel(eraser)


if __name__ == "__main__":
    """ This window can be used by itself for debugging purposes.
    """
    app = QApplication(sys.argv)
    window = BonusBrush()
    window.show()
    app.exec()
