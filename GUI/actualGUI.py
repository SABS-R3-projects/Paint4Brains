import sys
from pyqtgraph.Qt import QtCore, QtGui
import nibabel as nib
from MainWindow import MainWindow
import numpy as np

file_x = 'segmented.nii'
xim = nib.load(file_x)
dat = xim.get_fdata()
dimension = dat.shape

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = MainWindow(dat)
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
