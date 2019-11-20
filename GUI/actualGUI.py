import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, \
    QVBoxLayout, QWidget
from pyqtgraph.Qt import QtCore, QtGui

import pyqtgraph as pg
import numpy as np
import nibabel as nib

file_x = "80yearold.nii"
xim = nib.load(file_x)
dat = xim.get_fdata()
dimension = dat.shape

kern = np.array([
    [0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0]
])


class Slider(QWidget):
    def __init__(self, minimum, maximum, parent=None):
        super(Slider, self).__init__(parent=parent)
        self.verticalLayout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Vertical)
        self.horizontalLayout.addWidget(self.slider)
        spacerItem1 = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
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


class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent=parent)
        self.horizontalLayout = QHBoxLayout(self)
        self.w1 = Slider(0, dimension[0] - 1)
        self.horizontalLayout.addWidget(self.w1)

        self.win = pg.GraphicsView()
        self.setWindowTitle('First attempt')
        self.horizontalLayout.addWidget(self.win)
        self.view = pg.ViewBox()
        self.view.setAspectLocked(True)
        self.win.setCentralItem(self.view)
        self.img = pg.ImageItem(dat[54] / np.max(dat[54]))
        self.view.addItem(self.img)
        self.w1.slider.valueChanged.connect(self.update_plot)
        self.img.setDrawKernel(kern, mask=kern, center=(1, 1), mode='add')

    def update_plot(self):
        i = self.w1.x
        self.view.removeItem(self.img)
        self.img = pg.ImageItem(dat[i] / (1 + np.max(dat[i])))
        self.view.addItem(self.img)
        self.img.setDrawKernel(kern, mask=kern, center=(1, 1), mode='add')


if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = Widget()
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
