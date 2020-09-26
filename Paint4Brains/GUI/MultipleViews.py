"""Multi Views Module

This file contains a class requried for creating additional viewing boxes.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.MultipleViews import MultipleViews
        buttons = MultipleViews()

"""

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QSpacerItem
from PyQt5 import QtGui, QtCore
from Paint4Brains.GUI.SideView import SideView


class MultipleViews(QWidget):
    """MultipleViews class for Paint4Brains.

    This class is requried for creating additional viewing boxes.

    Args:
        main_widget (class): MainWidget class
        parent (class): Base or parent class
    """

    def __init__(self, main_widget, parent=None):
        super(MultipleViews, self).__init__(parent=parent)
        self.main_widget = main_widget
        self.mainview = main_widget.win
        self.brain = self.mainview.brain

        self.layout = QVBoxLayout(self)

        self.win1 = SideView(1, parent=self)
        self.win2 = SideView(2, parent=self)

        self.setFixedWidth(250)
        self.setMinimumHeight(540)
        space = QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        space2 = QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addSpacerItem(space2)
        self.layout.addWidget(self.win1)
        self.layout.addSpacerItem(space)
        self.layout.addWidget(self.win2)
        self.layout.addSpacerItem(space2)

    def set_views(self, position):
        """Function setting views

        This function sets the position for the different views

        Args:
            position (tuple): Tuple containing the required coordinates.
        """
        eachdim = [0 < position[i] < self.brain.shape[i] for i in range(3)]
        out_of_box = not (eachdim[0] and eachdim[1] and eachdim[2])
        self.win1.set_i(position, out_of_box)
        self.win1.refresh_image()
        self.win2.set_i(position, out_of_box)
        self.win2.refresh_image()
