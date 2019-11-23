from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
import numpy as np
from GUI.Slider import Slider
from GUI.PlaneSelectionButtons import PlaneSelectionButtons
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

pen = np.array([
    [0, 0, 0],
    [0, 1, 0],
    [0, 0, 0]
]).astype(np.uint8)


class MainWindow(QWidget):
    def __init__(self, data, labels, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.verticalLayout = QVBoxLayout()
        self.section = 0
        self.w1 = Slider(0, data.shape[self.section] - 1)
        self.w1.slider.setMaximum(data.shape[self.section] - 1)
        self.i = int(data.shape[self.section] / 2)
        self.label_data = labels
        self.data = data
        self.maxim = np.max(data)
        self.win = pg.GraphicsView()

        self.over_img = pg.ImageItem(self.get_label_data(self.i), autoDownSmaple=False, opacity=0.3,
                                     compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.img = pg.ImageItem(self.get_data(self.i) / self.maxim, autoDownsample=False,
                                compositionMode=QtGui.QPainter.CompositionMode_SourceOver)
        self.buttons = PlaneSelectionButtons(self.update0, self.update1, self.update2)

        # Making a Color Lookup Table for labelled data
        lut = np.array([[0, 0, 0, 0], [1, 245, 240, 255]])
        self.over_img.setLookupTable(lut)

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
        self.view.addItem(self.over_img)
        self.w1.slider.valueChanged.connect(self.update_after_slider)
        self.over_img.setDrawKernel(pen, mask=pen, center=(1, 1), mode='add')

    def get_data(self, i):
        if self.section == 0:
            return self.data[i]
        elif self.section == 1:
            return np.flip(self.data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.data[:, :, i].transpose(), axis=1)

    def get_label_data(self, i):
        if self.section == 0:
            return self.label_data[i]
        elif self.section == 1:
            return np.flip(self.label_data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.label_data[:, :, i].transpose(), axis=1)

    def set_label_data(self, i, x):
        if self.section == 0:
            self.label_data[i] = x
        elif self.section == 1:
            self.label_data[:, i] = np.flip(x.transpose())
        elif self.section == 2:
            self.label_data[:, :, i] = np.flip(x.transpose(), axis=1)

    def update_after_slider(self):
        self.label_data = np.clip(self.label_data, 0, 1)
        self.i = self.w1.x
        self.img.setImage(self.get_data(self.i) / self.maxim)
        self.over_img.setImage(self.get_label_data(self.i))
        self.over_img.setDrawKernel(pen, mask=pen, center=(1, 1), mode='add')

    def update_section_helper(self):
        self.label_data = np.clip(self.label_data, 0, 1)
        self.i = int(self.data.shape[self.section] / 2)
        self.w1.maximum = self.data.shape[self.section] - 1
        self.w1.slider.setMaximum(self.data.shape[self.section] - 1)
        self.img.setImage(self.get_data(self.i) / self.maxim)
        self.over_img.setImage(self.get_label_data(self.i))
        self.over_img.setDrawKernel(pen, mask=pen, center=(1, 1), mode='add')

    def update0(self):
        self.section = 0
        self.update_section_helper()

    def update1(self):
        self.section = 1
        self.update_section_helper()

    def update2(self):
        self.section = 2
        self.update_section_helper()
