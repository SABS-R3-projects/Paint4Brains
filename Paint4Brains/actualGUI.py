import sys
from pyqtgraph.Qt import QtCore, QtGui
import os
os.environ['KMP_WARNINGS'] = 'off'
from Paint4Brains.GUI.MainWindow import MainWindow

# checks if there are any extra parameters when calling python and assigns it to file_x or file_y if there is
file_y = None
if len(sys.argv) == 2:
    file_x = sys.argv[1]
elif len(sys.argv) > 2:
    file_x = sys.argv[1]
    file_y = sys.argv[2]
else:
    file_x = None

if __name__ == '__main__':
    # Basically just runs the MainWindow class
    app = QtGui.QApplication([])
    w = MainWindow(file_x, file_y)
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
