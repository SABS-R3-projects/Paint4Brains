"""GUI Main Widget

This file contains a collection of functions relevant to defining the maing widget properties of the GUI.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.MainWidget import MainWidget
        main_widget = MainWidget(parameters)

"""

import numpy as np
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QLabel
from PyQt5 import QtCore
from deepbrain import Extractor
from Paint4Brains.GUI.NormalizationWidget import NormalizationWidget
from Paint4Brains.GUI.PlaneSelectionButtons import PlaneSelectionButtons
from Paint4Brains.GUI.ImageViewer import ImageViewer
from Paint4Brains.GUI.MultipleViews import MultipleViews
from Paint4Brains.GUI.Slider import Slider


class MainWidget(QWidget):
    """MainWidget class for Paint4Brains.

    This class contains the implementation of a series of functions required for the GUI of the Paint4Brains project.

    Args:
        brain (class): BrainData class for Paint4Brains 
        parent (class): Base or parent class
    """

    def __init__(self, brain, parent=None):
        super(MainWidget, self).__init__(parent=parent)

        # Inputting data
        self.brain = brain

        # Creating viewing box to see data
        self.win = ImageViewer(self.brain)

        # Adding the additional viewing boxes
        self.buttons = MultipleViews(self)
        self.static = False

        # Creating a slider to go through image slices
        self.widget_slider = Slider(
            0, self.brain.shape[self.brain.section] - 1)
        self.widget_slider.slider.setMaximum(
            self.brain.shape[self.brain.section] - 1)
        self.widget_slider.slider.setValue(self.brain.i)
        self.widget_slider.slider.valueChanged.connect(
            self.update_after_slider)

        # Creating a label that tracks the position
        self.position = QLabel()
        self.position.setAlignment(QtCore.Qt.AlignRight)
        self.win.scene().sigMouseMoved.connect(self.mouse_tracker)

        # Arranging the layout
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.buttons)
        self.horizontalLayout.addWidget(self.win)

        self.verticalLayout = QVBoxLayout(self)
        spacerItem = QSpacerItem(
            10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout.addSpacerItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.widget_slider)
        self.verticalLayout.addWidget(self.position)

    def mouse_tracker(self, pos):
        """Mouse position tracker

        Tracks mouse and prints 3-D position to a label

        Args:
            pos (class): QPointF class defining a point in the plane using floating point precision
        """
        mouse_x = int(self.win.img.mapFromScene(pos).x())
        mouse_y = int(self.win.img.mapFromScene(pos).y())
        self.position.setText(
            str(self.brain.position_as_voxel(mouse_x, mouse_y)))

        if not self.static:
            self.buttons.set_views(
                self.brain.position_as_voxel(mouse_x, mouse_y))

    def update_after_slider(self):
        """Updates the viewed image after moving the slider.

        Updates the displayed slice depending on the new value of the slider.
        It does this for both the labels and image data.
        """
        self.brain.i = self.widget_slider.x
        self.win.refresh_image()

    def _update_section_helper(self):
        """Helper function used to ensure that everything runs smoothly after the view axis is changed.

        Ensures that the viewed slice exists;
        Sets the slider limits to sensible values;
        Updates the view of label and image data.
        """
        self.widget_slider.maximum = self.brain.shape[self.brain.section] - 1
        self.widget_slider.slider.setMaximum(
            self.brain.shape[self.brain.section] - 1)
        self.win.refresh_image()
        self.win.recenter()

    def update0(self):
        """Sets the view along axis 0

        This affects both labels and image data.
        This function is called by the first button.
        """
        self.brain.section = 0
        self._update_section_helper()

    def update1(self):
        """Sets the view along axis 1

        This affects both labels and image data.
        This function is called by the second button.
        """
        self.brain.section = 1
        self._update_section_helper()

    def update2(self):
        """Sets the view along axis 2

        This affects both labels and image data.
        This function is called by the third button.
        """
        self.brain.section = 2
        self._update_section_helper()

    def normalize_intensity(self):
        """Normalize intensity method

        A Method that calls the log_normalization method on the brain
        """
        self.brain.log_normalization()
        self.win.refresh_image()

    def extract(self):
        """Brain extractor

        Performs brain extraction using the DeepBrain neural network

        This extraction produces a probability mask.
        The current implementation is hard coded, to keep voxels with probability larger than a half.
        If the brain has already been extracted it loads a previous version.

        Functionality for this method is defined in the BrainData class.
        This wrapper has been kept here to ensure the displayed image is updated.
        """
        self.brain.brainExtraction()
        self.win.refresh_image()

    def full_brain(self):
        """Returns the image to the original brain and head image

        Returns the background image to the unextracted brain.
        Stores the extracted brain.

        Functionality for this method is defined in the BrainData class.
        This wrapper has been kept here to ensure the displayed image is updated.
        """
        self.brain.full_brain()
        self.win.refresh_image()

    def revert_to_old_buttons(self):
        """Revert to old buttons

        Function which if triggered, reverts to the old button layoyt and style
        """
        if not self.static:
            self.horizontalLayout.removeWidget(self.buttons)
            self.buttons.setVisible(False)
            self.buttons = PlaneSelectionButtons(
                self.update0, self.update1, self.update2)
            self.buttons.setVisible(True)
            self.horizontalLayout.insertWidget(0, self.buttons)
            self.static = True

        elif self.static:
            self.horizontalLayout.removeWidget(self.buttons)
            self.buttons.setVisible(False)
            self.buttons = MultipleViews(self)
            self.buttons.setVisible(True)
            self.horizontalLayout.insertWidget(0, self.buttons)
            self.static = False

    def wheelEvent(self, a0):
        """Wheel event editor

        Edits the behaviour of the mouse wheel.

        Functionality for this method is defined in the ImageViewer class.
        This wrapper has been kept here to ensure the slider position is updated.
        """
        self.widget_slider.slider.setValue(self.brain.i)
        super(MainWidget, self).wheelEvent(a0)
