import sys
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtGui import QPalette, QColor
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

    darkPalette = QPalette()

    # base
    darkPalette.setColor(QPalette.WindowText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.Light, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Midlight, QColor(90, 90, 90))
    darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.Text, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.BrightText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Link, QColor(56, 252, 196))
    darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))

    # disabled
    darkPalette.setColor(QPalette.Disabled, QPalette.WindowText,
                         QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Disabled, QPalette.Text,
                         QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText,
                         QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Disabled, QPalette.Highlight,
                         QColor(80, 80, 80))
    darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                         QColor(127, 127, 127))

    app.setStyle("Breeze")
    app.setPalette(darkPalette)
    app.setStyleSheet(open("style2.qss", "r").read())

    w = MainWindow(file_x, file_y)
    w.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
