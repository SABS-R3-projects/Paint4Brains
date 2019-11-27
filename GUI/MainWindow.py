from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QMainWindow
import numpy as np
from Slider import Slider
from PlaneSelectionButtons import PlaneSelectionButtons
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

cross = np.array([
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]).astype(np.uint8)

dot = np.array([[1]]).astype(np.uint8)


class MainWindow(QMainWindow):
    def __init__(self, data, labels, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        # Creating a central widget to take everything in
        self.central = QWidget()
        self.setCentralWidget(self.central)

        # Creating viewing box to see data
        self.setWindowTitle('First attempt')
        self.win = pg.GraphicsView()
        self.view = pg.ViewBox()
        self.view.setAspectLocked(True)
        self.win.setCentralItem(self.view)

        # Inputting data
        self.label_data = labels
        self.data = data
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
        self.over_img.setDrawKernel(dot, mask=dot, center=(0, 0), mode='add')

        # Creating a slider to go through image slices
        self.w1 = Slider(0, data.shape[self.section] - 1)
        self.w1.slider.setMaximum(data.shape[self.section] - 1)
        self.w1.slider.setValue(self.i)
        self.w1.slider.valueChanged.connect(self.update_after_slider)

        # Arranging the layout
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.buttons)
        self.horizontalLayout.addWidget(self.win)

        self.verticalLayout = QVBoxLayout(self.central)
        spacerItem = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout.addSpacerItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.w1)

        # Making a menu
        self.statusBar()
        menu_bar = self.menuBar()
        self.file = menu_bar.addMenu("File")
        self.file = menu_bar.addMenu("Edit")
        self.view_menu = menu_bar.addMenu("View")
        self.extra_menu = menu_bar.addMenu("This is intentionally very long to see what happens")

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

    def update_section_helper(self):
        self.label_data = np.clip(self.label_data, 0, 1)
        self.i = int(self.data.shape[self.section] / 2)
        self.w1.maximum = self.data.shape[self.section] - 1
        self.w1.slider.setMaximum(self.data.shape[self.section] - 1)
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
