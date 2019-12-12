from PyQt5.QtWidgets import QHBoxLayout, QWidget, QPushButton
from pyqtgraph.Qt import QtCore, QtGui


class EditingButtons(QWidget):
    """
    Class to create buttons for editing the brain extracted MRI image
    """
    def __init__(self, function_list,icon_list, parent=None):
        super(EditingButtons, self).__init__(parent=parent)
        """ Initialises the specified number of buttons on the top of the main widget
        These include a dot/pen for editing segmented areas and a rubber for erasing segmented areas
        params: 
            button_list is a list of functions called when you click the button
            icon_list is a list with names of the icons for the buttons 
        """
        self.button = []
        self.layout = QHBoxLayout(self)
        for i, buttons in enumerate(function_list):
            #self.btn1 = QPushButton()
            bt = QPushButton()
            bt.setIcon(QtGui.QIcon(icon_list[i]))
            bt.setFixedSize(30, 30)
            bt.setIconSize(QtCore.QSize(25, 25))
            self.button.append(bt)
            self.layout.addWidget(bt)
            bt.clicked.connect(buttons)

        self.layout.setSpacing(0)
