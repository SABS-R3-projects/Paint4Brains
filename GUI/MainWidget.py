from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QMainWindow, QAction, qApp
import numpy as np
from Slider import Slider
from PlaneSelectionButtons import PlaneSelectionButtons
from ModViewBox import ModViewBox
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

cross = np.array([
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]).astype(np.uint8)

dot = np.array([[1]]).astype(np.uint8)


class MainWidget(QWidget):
    def __init__(self, data, labels, parent=None):
        super(MainWidget, self).__init__(parent=parent)
        # Creating a central widget to take everything in

        # Creating viewing box to see data
        self.win = pg.GraphicsView()
        self.view = ModViewBox()
        self.view.setAspectLocked(True)
        self.win.setCentralItem(self.view)

        # Inputting data
        self.label_data = np.zeros(data.shape) #np.flip(labels.transpose())
        self.data = np.flip(data.transpose())
        self.maxim = np.max(data)
        self.section = 0
        self.i = int(data.shape[self.section] / 2)

        # Making Images out of data
        self.over_img = pg.ImageItem(self.get_label_data(self.i), autoDownSmaple=False, opacity=0.3,
                                     compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.img = pg.ImageItem(self.get_data(self.i) / self.maxim, autoDownsample=False,
                                compositionMode=QtGui.QPainter.CompositionMode_SourceOver)
        self.buttons = PlaneSelectionButtons(self.update0, self.update1, self.update2)

        # Colouring the labelled data
        lut = np.array([[0, 0, 0, 0], [1, 245, 240, 255]])
        self.over_img.setLookupTable(lut)

        # Adding the images and setting it to drawing mode
        self.view.addItem(self.img)
        self.view.addItem(self.over_img)

        # Creating a slider to go through image slices
        self.widget_slider = Slider(0, data.shape[self.section] - 1)
        self.widget_slider.slider.setMaximum(data.shape[self.section] - 1)
        self.widget_slider.slider.setValue(self.i)
        self.widget_slider.slider.valueChanged.connect(self.update_after_slider)

        # Arranging the layout
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.buttons)
        self.horizontalLayout.addWidget(self.win)

        self.verticalLayout = QVBoxLayout(self)
        spacerItem = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout.addSpacerItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.widget_slider)

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

    def load_label_data(self, x):
        self.label_data = x #np.flip(x.transpose())
        self.over_img.setDrawKernel(dot, mask=dot, center=(0, 0), mode='add')
        self.view.drawing = True

    def update_after_slider(self):
        self.label_data = np.clip(self.label_data, 0, 1)
        self.i = self.widget_slider.x
        self.img.setImage(self.get_data(self.i) / self.maxim)
        self.over_img.setImage(self.get_label_data(self.i))

    def update_section_helper(self):
        self.label_data = np.clip(self.label_data, 0, 1)
        self.i = int(self.data.shape[self.section] / 2)
        self.widget_slider.maximum = self.data.shape[self.section] - 1
        self.widget_slider.slider.setMaximum(self.data.shape[self.section] - 1)
        self.img.setImage(self.get_data(self.i) / self.maxim)
        self.over_img.setImage(self.get_label_data(self.i))

    def update0(self):
        self.section = 0
        self.update_section_helper()

    def update1(self):
        self.section = 1
        self.update_section_helper()

    def update2(self):
        self.section = 2
        self.update_section_helper()

    def unsetDrawKernel(self):
        self.over_img.drawKernel = None
        self.view.drawing = False
