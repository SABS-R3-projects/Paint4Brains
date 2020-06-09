from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QSizePolicy, QSpacerItem
import pyqtgraph as pg
import numpy as np
import nibabel as nib
import os
os.chdir("/home/sabs-r3/Desktop")


class HistogramWidget(QWidget):

    def __init__(self, viewer):
        self.win = viewer
        super(HistogramWidget, self).__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.graphWidget = pg.PlotWidget()
        self.setFixedWidth(300)
        self.setMinimumHeight(400)
        space = QSpacerItem(300, 500, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.graphWidget = pg.PlotWidget(title='Histogram')
        brain = nib.load("77year_Pipe.nii")
        brain_data = brain.get_fdata()
        y, x = np.histogram(brain_data, bins=255, range=(1, 255), density=False)
        y = y / 100000.0
        self.graphWidget.plot(x[:-1], y, pen=2, symbol = 'o', symbolSize=1)
        self.graphWidget.setLabel('left', 'Intensity', color='red', size=30)
        self.graphWidget.setLabel('bottom', 'Pixels', color='red', size=30)
        self.layout.addWidget(self.graphWidget)
        self.layout.addSpacerItem(space)
