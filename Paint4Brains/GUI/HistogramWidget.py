from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QSizePolicy, QSpacerItem, QVBoxLayout
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import sys
import numpy as np
import nibabel as nib
import os
from pyqtgraph import ViewBox

os.chdir("/home/sabs-r3/Desktop")
from Paint4Brains.BrainData import BrainData


class HistogramWidget(QWidget):

    def __init__(self, viewer, minimum=0.5, maximum=1.6):
        self.win = viewer
        super(HistogramWidget, self).__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.graphWidget = pg.PlotWidget()

        #self.setCentralWidget(self.graphWidget)
        # brain = nib.load("77year_Pipe.nii")
        # brain_data = brain.get_fdata()
        #
        # y, x = np.histogram(brain_data, bins=255, range=(1, 255), density=False)
        # self.graphWidget.plot(x[:-1], y, pen=2)
        # dockWidget = QDockWidget('Histogram', self)
        # dockWidget.setWidget(self.graphWidget)
        # self.addDockWidget(Qt.RightDockWidgetArea, dockWidget)

        self.setFixedWidth(300)
        self.setMinimumHeight(400)


        # self.layout.addSpacerItem(space)
        space = QSpacerItem(300, 500, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.graphWidget = pg.PlotWidget(title='Histogram')
        brain = nib.load("77year_Pipe.nii")
        brain_data = brain.get_fdata()
        y, x = np.histogram(brain_data, bins=255, range=(1, 255), density=False)
        y = y / 100000.0
        self.graphWidget.plot(x[:-1], y, pen=2)
        self.graphWidget.setLabel('left', 'Intensity (x10 000)', color='red', size=30)
        self.graphWidget.setLabel('bottom', 'Pixels', color='red', size=30)
        # self.layout.addSpacerItem(space)
        # dockWidget = QDockWidget('Histogram', self)
        # dockWidget.setWidget(self.graphWidget)
        #self.layout.addSpacerItem(space)
        self.layout.addWidget(self.graphWidget)

        self.layout.addSpacerItem(space)

# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     main = HistogramWidget()
#     #main.resize(50, 50)
#     main.show()
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#     main()