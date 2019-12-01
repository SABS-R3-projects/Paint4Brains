import sys
from pyqtgraph.Qt import QtCore, QtGui
import nibabel as nib
from MainWindow import MainWindow
import numpy as np

if len(sys.argv) > 1:
    file_x = sys.argv[1]
else:
    file_x = None


if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = MainWindow(file_x)
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
