import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, \
    QVBoxLayout, QWidget, QPushButton
from pyqtgraph.Qt import QtCore, QtGui

import pyqtgraph as pg
import numpy as np
import nibabel as nib

file_x = "80yearold.nii"
xim = nib.load(file_x)
dat = xim.get_fdata()

kern = np.array([
    [0.0, 0.0, 0.0],
    [0.0, 0.2, 0.0],
    [0.0, 0.0, 0.0]
])


class ViewButtons(QWidget):
    def __init__(self, button1, button2, button3, parent=None):
        super(ViewButtons, self).__init__(parent=parent)

        self.layout = QVBoxLayout(self)
        self.btn1 = QPushButton()
        self.btn1.setIcon(QtGui.QIcon('one.png'))
        self.btn1.setIconSize(QtCore.QSize(100, 100))
        self.btn2 = QPushButton("button2")
        self.btn3 = QPushButton("button3")

        self.btn1.setFixedSize(100, 100)
        self.btn2.setFixedSize(100, 100)
        self.btn3.setFixedSize(100, 100)

        self.layout.addWidget(self.btn1)
        self.layout.addWidget(self.btn2)
        self.layout.addWidget(self.btn3)
        self.layout.setSpacing(20)

        self.btn1.clicked.connect(button1)
        self.btn2.clicked.connect(button2)
        self.btn3.clicked.connect(button3)


class Slider(QWidget):
    def __init__(self, minimum, maximum, parent=None):
        super(Slider, self).__init__(parent=parent)
        self.verticalLayout = QHBoxLayout(self)
        self.label = QLabel(self)
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QVBoxLayout()
        spacerItem = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.slider = QSlider(self)
        self.slider.setMinimum(0)
        self.slider.setOrientation(Qt.Horizontal)
        self.horizontalLayout.addWidget(self.slider)
        spacerItem1 = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.resize(self.sizeHint())

        self.minimum = minimum
        self.maximum = maximum
        self.slider.valueChanged.connect(self.setLabelValue)
        self.x = None
        self.setLabelValue(self.slider.value())

    def setLabelValue(self, value):
        self.x = int(self.minimum + (float(value) / (self.slider.maximum() - self.slider.minimum())) * (
                self.maximum - self.minimum))
        self.label.setText("Slice: \n{0:.4g}".format(self.x))


class Window(QWidget):
    def __init__(self, data, parent=None):
        super(Window, self).__init__(parent=parent)
        self.verticalLayout = QVBoxLayout()
        self.section = 0
        self.w1 = Slider(0, data.shape[0] - 1)
        self.w1.slider.setMaximum(data.shape[0] - 1)
        self.i = int(data.shape[0] / 2)
        self.data = data
        self.maxim = np.max(data)
        self.win = pg.GraphicsView()
        self.img = pg.ImageItem(self.data[self.i] / self.maxim)
        self.buttons = ViewButtons(self.update0, self.update1, self.update2)

        self.setWindowTitle('First attempt')
        self.verticalLayout.addWidget(self.win)
        self.verticalLayout.addWidget(self.w1)

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.addWidget(self.buttons)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.view = pg.ViewBox()
        self.view.setAspectLocked(True)
        self.win.setCentralItem(self.view)
        self.view.addItem(self.img)
        self.w1.slider.valueChanged.connect(self.update_after_slider)
        self.img.setDrawKernel(kern, mask=kern, center=(1, 1), mode='add')

    def update_after_slider(self):
        self.data[self.i] = self.img.image
        self.i = self.w1.x
        self.img.setImage(self.data[self.i] / self.maxim)
        self.img.setDrawKernel(kern, mask=kern, center=(1, 1), mode='add')

    def update_section_helper(self, dimen):
        self.data[self.i] = self.img.image
        if (dimen - self.section)%3 == 1:
            self.data = np.transpose(self.data,(2,0,1))
        if (dimen - self.section)%3 == 2:
            self.data = np.transpose(self.data,(1,2,0))
        self.section = dimen
        self.i = int(self.data.shape[0] / 2)
        self.w1.maximum = self.data.shape[0] - 1
        self.w1.slider.setMaximum(self.data.shape[0] - 1)
        self.img.setImage(self.data[self.i] / self.maxim)
        self.img.setDrawKernel(kern, mask=kern, center=(1, 1), mode='add')

    def update0(self):
        self.update_section_helper(0)

    def update1(self):
        self.update_section_helper(1)

    def update2(self):
        self.update_section_helper(2)





if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = Window(dat)
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
