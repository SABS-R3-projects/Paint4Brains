from fbs_runtime.application_context.PyQt5 import ApplicationContext
import sys
from pyqtgraph.Qt import QtCore, QtGui
import os
os.environ['KMP_WARNINGS'] = 'off'
from MainWindow import MainWindow
from Styler import palette, style

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
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    app = appctxt.app
    app.setStyle("Fusion")
    app.setPalette(palette())
    app.setStyleSheet(style())

    w = MainWindow(file_x, file_y)
    w.show()
    exit_code = app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
