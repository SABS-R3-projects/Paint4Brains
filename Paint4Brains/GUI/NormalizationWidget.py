"""Normalization Widget Module

This file contains a class requried for creating the Intensity Normalization widget.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.NormalizationWidget import NormalizationWidget
        norm_widget = NormalizationWidget(parameters)

"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QSizePolicy, QSpacerItem, QVBoxLayout, QDockWidget
import nibabel as nib
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt

class NormalizationWidget(QWidget):
    """NormalizationWidget class

    A class that creates the Intensity Normalization widget that appears when Adjust Intensity option under the Tools menu bar is clicked.

    Args:
        viewer (class): ImageViewer class
        minimum (float): Minimum normalization value
        maximum (float): Maximum normalization value
    """

    def __init__(self, viewer, minimum=0.5, maximum=1.6):
        self.win = viewer
        self.brain = viewer.brain
        self.histogram_below = False

        _translate = QtCore.QCoreApplication.translate
        super(NormalizationWidget, self).__init__()

        self.setMinimumWidth(200)
        self.setMaximumHeight(100)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setObjectName("tabWidget")
        self.layout.addWidget(self.tabWidget)
        self.minimum = minimum
        self.maximum = maximum
        self.intensity = None
        self.verticalLayout = QVBoxLayout()


        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, 'Log Adjust')
        self.tab_layout = QtWidgets.QVBoxLayout(self.tab)

        self.label = QtWidgets.QLabel(self.tab)
        self.label.setObjectName("Log")
        self.label.setText(_translate("MainWindow", "Adjust Intensity"))
        self.tab_layout.addWidget(self.label)

        self.log_intensity_slider = QtWidgets.QSlider(self.tab)
        self.log_intensity_slider.setOrientation(QtCore.Qt.Horizontal)
        self.log_intensity_slider.setObjectName("log_intensity_slider")
        self.log_intensity_slider.setMinimum(0)
        self.log_intensity_slider.setValue(1)
        self.tab_layout.addWidget(self.log_intensity_slider)
        self.log_intensity_slider.valueChanged.connect(self.update_intensity)

#######################
        # self.setFixedWidth(300)
        # self.setMinimumHeight(800)
        #
        # #self.layout.addSpacerItem(space)
        # space = QSpacerItem(200, 700, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.graphWidget = pg.PlotWidget(title = 'Histogram')
        # brain = nib.load("77year_Pipe.nii")
        # brain_data = brain.get_fdata()
        # y, x = np.histogram(brain_data, bins=255, range=(1, 255), density=False)
        # y = y/100000.0
        # self.graphWidget.plot(x[:-1], y, pen=2)
        # self.graphWidget.setLabel('left', 'Intensity (x10 000)', color='red', size=30)
        # self.graphWidget.setLabel('bottom', 'Pixels', color='red', size=30)
        # #self.layout.addSpacerItem(space)
        # #dockWidget = QDockWidget('Histogram', self)
        # #dockWidget.setWidget(self.graphWidget)
        # self.layout.addWidget(self.graphWidget)
        #
        # self.layout.addSpacerItem(space)



###################


    def update_intensity(self):
        """Intensity Update

        A Method that keeps track of the intensity values displayed on the Logarithmic Intensity Widget
        It updates the appearance of the brain on the viewer as intensity is changed
        """
        # Take input from controller
        value = self.log_intensity_slider.value()
        self.brain.intensity = (self.minimum + (
            float(value) / (self.log_intensity_slider.maximum() - self.log_intensity_slider.minimum())) * (
            self.maximum - self.minimum))
        # Edit the Brain Data Using function defined in BrainData class
        self.brain.log_normalization()
        # Update what you are displaying
        self.label.setText(
            "Intensity Level: {0:.1f}".format(self.brain.intensity))
        self.win.refresh_image()
