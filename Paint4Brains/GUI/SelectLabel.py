"""Select Label Module

This file contains a collection of functions which allow the user to select different labels after the segmentation operation.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.SelectLabel import SelectLabel
        dropbox = SelectLabel(properties)

"""

from Paint4Brains import Segmenter
from PyQt5.QtWidgets import QComboBox, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy


class SelectLabel(QWidget):
    """SelectLabel class

    Drop-down box used to select which region of the brain you want to edit and visualize.
    Passing the ImageViewer class allows the drop-down box to refresh the displayed image.

    Args:
        window (class): ImageViewer class
        parent (class): Base or parent class

    """

    def __init__(self, window, parent=None):
        super(SelectLabel, self).__init__(parent=parent)
        self.brain = window.brain
        self.window = window
        self.new_layout = QHBoxLayout(self)
        self.dropbox = QComboBox()
        space = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.new_layout.addItem(space)
        self.new_layout.addWidget(self.dropbox)
        self.names = Segmenter.label_names
        for name in self.names[2:]:
            self.dropbox.addItem(name)
        self.dropbox.currentIndexChanged.connect(self.update_brain)

    @property
    def current_index(self):
        """Current index

        Function determining the current index.

        Returns:
            int: Incremented current index
        """

        return self.dropbox.currentIndex() + 1

    @current_index.setter
    def current_index(self, i):
        """Current index setter

        Function setting the current index.

        Args:
            i (int): Current index 

        Returns:
            int: Incremented current index
        """
        self.dropbox.setCurrentIndex(i - 1)

    def update_brain(self):
        """Label update

        Updates the selected label if the value in the dropdown box is changed
        """
        self.brain.current_label = self.current_index
        self.window.refresh_image()

    def update_box(self):
        """Dropdown box update

        Updates the value in the dropdown box if the selected brain label is changed by other means
        """
        self.current_index = self.brain.current_label

