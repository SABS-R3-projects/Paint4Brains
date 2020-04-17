"""Paint4Brains GUI Run File

This is the main run function of the Paint4Brains software. In order to run the software, a user must run this script. 

Attributes:
    file_x (str): Path leading to the location of the brain data file.
    file_y (str): Path to the location of the labeled data file.
    app (class): PyQT5 class which manages the GUI application's control flow and main settings.
    w (class): Internal class controlling the main window of the gui.

Usage:
    Before running, make sure that you are in an environment. This can be setup and ran using the following:

        $ ./setup.sh
        $ source env/bin/activate

    Then, simply call the function:

        $ python Paint4Brains/actualGUI.py 

"""


from Paint4Brains.GUI.Styler import palette, style
from Paint4Brains.GUI.MainWindow import MainWindow
import sys
from pyqtgraph.Qt import QtCore, QtGui
import os
os.environ['KMP_WARNINGS'] = 'off'

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
    app.setStyle("Fusion")
    app.setPalette(palette())
    app.setStyleSheet(style())

    w = MainWindow(file_x, file_y)
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
