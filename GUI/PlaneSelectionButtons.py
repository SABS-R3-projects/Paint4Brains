from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton
from pyqtgraph.Qt import QtCore, QtGui
from fbs_runtime.application_context.PyQt5 import ApplicationContext

app = ApplicationContext()

class PlaneSelectionButtons(QWidget):
    """
    Plane selection Buttons class.
    Implements the buttons with which you can pick the brain view orientation
    """
    def __init__(self, button1, button2, button3, parent=None):
        super(PlaneSelectionButtons, self).__init__(parent=parent)
        """ Initialises the 3 buttons on the left side 
        Basically a number of QT buttons arranged in a vertical layout. When the class is initialised the three 
        functions to be executed when pressing the buttons are given as input. The buttons are decorated with images
        and I have fixed the size.
        """
        self.layout = QVBoxLayout(self)
        self.btn1 = QPushButton()
        p1 = app.get_resource('images/one.png')
        self.btn1.setIcon(QtGui.QIcon(p1))
        self.btn1.setIconSize(QtCore.QSize(100, 100))
        self.btn2 = QPushButton()
        p2 = app.get_resource('images/two.png')
        self.btn2.setIcon(QtGui.QIcon(p2))
        self.btn2.setIconSize(QtCore.QSize(100, 100))
        self.btn3 = QPushButton()
        p3 = app.get_resource('images/three.png')
        self.btn3.setIcon(QtGui.QIcon(p3))
        self.btn3.setIconSize(QtCore.QSize(100, 100))


        self.btn1.setFixedSize(120, 120)
        self.btn2.setFixedSize(120, 120)
        self.btn3.setFixedSize(120, 120)

        self.layout.addWidget(self.btn1)
        self.layout.addWidget(self.btn2)
        self.layout.addWidget(self.btn3)
        self.layout.setSpacing(20)

        self.btn1.clicked.connect(button1)
        self.btn2.clicked.connect(button2)
        self.btn3.clicked.connect(button3)
