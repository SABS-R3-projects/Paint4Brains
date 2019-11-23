import sys
from pyqtgraph.Qt import QtCore, QtGui
import nibabel as nib
from GUI.MainWindow import MainWindow

file_x = "segmented.nii"
file_y = "segmented_left_hippo.nii"
xim = nib.load(file_x)
yim = nib.load(file_y)
lab_dat = yim.get_data()
dat = xim.get_fdata()
dimension = dat.shape

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = MainWindow(dat, lab_dat)
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
