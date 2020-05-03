from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys
import numpy as np
import nibabel as nib
import os
os.chdir("/home/sabs-r3/Desktop")

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        brain = nib.load("77year_Pipe.nii")
        brain_data = brain.get_fdata()
        y, x = np.histogram(brain_data, bins=255, range=(1, 255), density=False)
        self.graphWidget.plot(x[:-1], y, pen=2)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()