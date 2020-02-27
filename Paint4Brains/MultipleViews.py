from pyqtgraph import ImageItem, GraphicsView, ViewBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QLabel
from PyQt5 import QtGui, QtCore
from SideView import SideView


class MultipleViews(QWidget):
    def __init__(self, main_widget, parent=None):
        super(MultipleViews, self).__init__(parent=parent)
        self.main_widget = main_widget
        self.mainview = main_widget.win
        self.brain = self.mainview.brain

        self.layout = QVBoxLayout(self)

        self.win1 = SideView(1, parent = self)
        self.win2 = SideView(2, parent = self)

        self.setFixedWidth(250)
        self.setMinimumHeight(500)
        space = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.layout.addWidget(self.win1)
        self.layout.addSpacerItem(space)
        self.layout.addWidget(self.win2)

    def set_views(self, position):
        eachdim = [0< position[i] < self.brain.shape[i] for i in range(3)]
        out_of_box = not (eachdim[0] and eachdim[1] and eachdim[2])
        self.win1.set_i(position, out_of_box)
        self.win1.refresh_image()
        self.win2.set_i(position, out_of_box)
        self.win2.refresh_image()

