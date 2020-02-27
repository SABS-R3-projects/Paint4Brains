import numpy as np
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QLabel
from PyQt5 import QtCore
from deepbrain import Extractor
from Slider import Slider
from PlaneSelectionButtons import PlaneSelectionButtons
from ImageViewer import ImageViewer
from MultipleViews import MultipleViews


class MainWidget(QWidget):
    def __init__(self, brain, parent=None):
        super(MainWidget, self).__init__(parent=parent)

        # Inputting data
        self.brain = brain

        # Creating viewing box to see data
        self.win = ImageViewer(self.brain)

        # Adding the plane selection buttons
        #self.buttons = PlaneSelectionButtons(self.update0, self.update1, self.update2)
        self.buttons = MultipleViews(self)

        # Creating a slider to go through image slices
        self.widget_slider = Slider(0, self.brain.shape[self.brain.section] - 1)
        self.widget_slider.slider.setMaximum(self.brain.shape[self.brain.section] - 1)
        self.widget_slider.slider.setValue(self.brain.i)
        self.widget_slider.slider.valueChanged.connect(self.update_after_slider)

        # Creating a label that tracks the position
        self.position = QLabel()
        self.position.setAlignment(QtCore.Qt.AlignRight)
        self.win.scene().sigMouseMoved.connect(self.mouse_tracker)

        # Arranging the layout
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.buttons)
        self.horizontalLayout.addWidget(self.win)

        self.verticalLayout = QVBoxLayout(self)
        spacerItem = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout.addSpacerItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.widget_slider)
        self.verticalLayout.addWidget(self.position)

    def mouse_tracker(self, pos):
        """ Tracks mouse and prints 3-D position to a label
        """
        mouse_x = int(self.win.img.mapFromScene(pos).x())
        mouse_y = int(self.win.img.mapFromScene(pos).y())
        self.position.setText(str(self.brain.position_as_voxel(mouse_x, mouse_y)))

        #New Code:

        self.buttons.set_views(self.brain.position_as_voxel(mouse_x, mouse_y))

    def update_after_slider(self):
        """ Updates the viewed image after moving the slider.

        Updates the displayed slice depending on the new value of the slider.
        It does this for both the labels and image data.
        """
        self.brain.i = self.widget_slider.x
        self.win.refresh_image()

    def _update_section_helper(self):
        """ Helper function used to ensure that everything runs smoothly after the view axis is changed.

        Ensures that the viewed slice exists;
        Sets the slider limits to sensible values;
        Updates the view of label and image data.
        """
        self.widget_slider.maximum = self.brain.shape[self.brain.section] - 1
        self.widget_slider.slider.setMaximum(self.brain.shape[self.brain.section] - 1)
        self.win.refresh_image()
        self.win.recenter()

    def update0(self):
        """ Sets the view along axis 0

        This affects both labels and image data.
        This function is called by the first button.
        """
        self.brain.section = 0
        self._update_section_helper()

    def update1(self):
        """ Sets the view along axis 1

        This affects both labels and image data.
        This function is called by the second button.
        """
        self.brain.section = 1
        self._update_section_helper()

    def update2(self):
        """ Sets the view along axis 2

        This affects both labels and image data.
        This function is called by the third button.
        """
        self.brain.section = 2
        self._update_section_helper()

    def extract(self):
        """ Performs brain extraction using the DeepBrain neural network

        This extraction produces a probability mask.
        At the moment it is hard coded such that we keep voxels with probability larger than a half.
        If the brain has already been extracted it loads a previous version.

        Functionality for this method is defined in the BrainData class.
        This wrapper has been kept here to ensure the displayed image is updated.
        """
        self.brain.brainExtraction()
        self.win.refresh_image()

    def full_brain(self):
        """ Returns the image to the original brain + head image

        Returns the background image to the unextracted brain.
        Stores the extracted brain.

        Functionality for this method is defined in the BrainData class.
        This wrapper has been kept here to ensure the displayed image is updated.
        """
        self.brain.full_brain()
        self.win.refresh_image()

    def wheelEvent(self, a0):
        """ Edits the behaviour of the mouse wheel.

        Functionality for this method is defined in the ImageViewer class.
        This wrapper has been kept here to ensure the slider position is updated.
        """
        self.widget_slider.slider.setValue(self.brain.i)
        super(MainWidget, self).wheelEvent(a0)
