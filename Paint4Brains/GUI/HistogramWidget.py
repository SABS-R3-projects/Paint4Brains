from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QSizePolicy, QSpacerItem
import pyqtgraph as pg
import numpy as np
import nibabel as nib
import os


class HistogramWidget(QWidget):

    def __init__(self, viewer):
        self.win = viewer
        self.brain = self.win.brain
        super(HistogramWidget, self).__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setWindowTitle("Intensity Correction Histogram")
        self.graphWidget = pg.PlotWidget()
        y, x = np.histogram(self.brain.data, bins=32, range=(1./256, 1.), density=True)
        self.graphWidget.plot(x, y, range=(1./256, 1.), density=True, stepMode=True)
        self.graphWidget.setLabel('left', 'Voxel Density', size=30)
        self.graphWidget.setLabel('bottom', 'Voxel Intensity', size=30)
        self.layout.addWidget(self.graphWidget)

        self.minimum = 0.5
        self.maximum = 1.6
        self.step_size = 0.1

        self.hlayout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel()
        self.label.setObjectName("Log")
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "Adjust Intensity"))
        self.hlayout.addWidget(self.label)

        self.log_intensity_slider = QtWidgets.QSlider()
        self.log_intensity_slider.setOrientation(QtCore.Qt.Horizontal)
        self.log_intensity_slider.setObjectName("log_intensity_slider")
        self.log_intensity_slider.setMinimum(int(self.minimum/self.step_size))
        self.log_intensity_slider.setMaximum(int(self.maximum/self.step_size))
        self.log_intensity_slider.setValue(int(1.0/self.step_size))
        self.log_intensity_slider.setSingleStep(1)
        self.hlayout.addWidget(self.log_intensity_slider)
        self.layout.addLayout(self.hlayout)
        self.log_intensity_slider.valueChanged.connect(self.update_intensity)

    def update_intensity(self):
        """Intensity Update

        A Method that keeps track of the intensity values displayed on the Logarithmic Intensity Widget
        It updates the appearance of the brain on the viewer as intensity is changed
        """
        # Take input from controller
        value = self.log_intensity_slider.value()
        self.brain.intensity = float(value) * self.step_size
        # Edit the Brain Data Using function defined in BrainData class
        self.brain.log_normalization()
        y, x = np.histogram(self.brain.data.flatten(), bins=32, range=(1./256, 1.), density=True)
        # Update what you are displaying on histogram window
        self.graphWidget.clear()

        self.graphWidget.plot(x, y, range=(1./256, 1.), stepMode=True, density=True)
        self.label.setText(
            "Intensity Level: {0:.1f}".format(self.brain.intensity))
        # Update what you are displaying on brain image
        self.win.refresh_image()
