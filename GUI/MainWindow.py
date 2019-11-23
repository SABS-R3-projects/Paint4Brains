from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
import numpy as np
from GUI.Slider import Slider
from GUI.PlaneSelectionButtons import PlaneSelectionButtons
import pyqtgraph as pg

pen = np.array([
    [0.0, 0.0, 0.0],
    [0.0, 0.2, 0.0],
    [0.0, 0.0, 0.0]
])


class MainWindow(QWidget):
    def __init__(self, data, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.verticalLayout = QVBoxLayout()
        self.section = 0
        self.w1 = Slider(0, data.shape[self.section] - 1)
        self.w1.slider.setMaximum(data.shape[self.section] - 1)
        self.i = int(data.shape[self.section] / 2)
        self.data = data
        self.maxim = np.max(data)
        self.win = pg.GraphicsView()
        self.img = pg.ImageItem(self.get_data(self.i) / self.maxim)
        self.buttons = PlaneSelectionButtons(self.update0, self.update1, self.update2)

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
        self.img.setDrawKernel(pen, mask=pen, center=(1, 1), mode='add')

    def get_data(self, i):
        if self.section == 0:
            return self.data[i]
        elif self.section == 1:
            return np.flip(self.data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.data[:, :, i].transpose(), axis=1)

    def set_data(self, i, x):
        if self.section == 0:
            self.data[i] = x
        elif self.section == 1:
            self.data[:, i] = np.flip(x.transpose())
        elif self.section == 2:
            self.data[:, :, i] = np.flip(x.transpose(), axis=1)

    def update_after_slider(self):
        # Causes many problems:
        # self.set_data(self.i, self.img.image)
        self.i = self.w1.x
        self.img.setImage(self.get_data(self.i) / self.maxim)
        self.img.setDrawKernel(pen, mask=pen, center=(1, 1), mode='add')

    def update_section_helper(self):
        self.i = int(self.data.shape[self.section] / 2)
        self.w1.maximum = self.data.shape[self.section] - 1
        self.w1.slider.setMaximum(self.data.shape[self.section] - 1)
        self.img.setImage(self.get_data(self.i) / self.maxim)
        self.img.setDrawKernel(pen, mask=pen, center=(1, 1), mode='add')

    def update0(self):
        self.section = 0
        self.update_section_helper()

    def update1(self):
        self.section = 1
        self.update_section_helper()

    def update2(self):
        self.section = 2
        self.update_section_helper()
