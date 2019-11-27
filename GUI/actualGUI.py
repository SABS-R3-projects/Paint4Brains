import sys
from pyqtgraph.Qt import QtCore, QtGui
import nibabel as nib
from MainWindow import MainWindow
import numpy as np

file_x = 'segmented.nii'
file_y = 'segmented_left_hippo.nii'
xim = nib.load(file_x)
yim = nib.load(file_y)
# 80 year old and manually segmented have different axis
lab_dat = np.flip(yim.get_data().transpose())
dat = np.flip(xim.get_fdata().transpose())
dimension = dat.shape

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = MainWindow(dat, lab_dat)
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
