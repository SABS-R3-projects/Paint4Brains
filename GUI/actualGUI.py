import sys
from pyqtgraph.Qt import QtCore, QtGui
from MainWindow import MainWindow

# checks if there are any extra parameters when calling python and assigns it to file_x if there is
if len(sys.argv) > 1:
    file_x = sys.argv[1]
else:
    file_x = None


if __name__ == '__main__':
    # Basically just runs the MainWindow class
    app = QtGui.QApplication([])
    w = MainWindow(file_x)
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
