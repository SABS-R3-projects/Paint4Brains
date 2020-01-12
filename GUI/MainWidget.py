import numpy as np
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QLabel
from PyQt5 import QtCore
from deepbrain import Extractor
from Slider import Slider
from PlaneSelectionButtons import PlaneSelectionButtons
from BrainData import BrainData
from ImageViewer import ImageViewer


class MainWidget(QWidget):
    def __init__(self, brain, parent=None):
        super(MainWidget, self).__init__(parent=parent)

        # Inputting data
        self.brain = brain

        # Creating viewing box to see data
        self.win = ImageViewer(self.brain)

        # Initialising some memory used by functions
        self.full_head = self.brain.data.copy()
        self.only_brain = []
        self.normalized = 0
        self.extracted = False
        self.segmented = False
        self.overlaid = False

        # Adding the plane selection buttons
        self.buttons = PlaneSelectionButtons(self.update0, self.update1, self.update2)

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

    def update_after_slider(self):
        """ Updates the viewed image after moving the slider.

        Updates the displayed slice depending on the new value of the slider.
        It does this for both the labels and image data.
        """
        self.brain.i = self.widget_slider.x
        self.win.refresh_image()

    def __update_section_helper(self):
        """ Helper function used to ensure that everything runs smoothly after the view axis is changed.

        Ensures that the viewed slice exists;
        Sets the slider limits to sensible values;
        Updates the view of label and image data.
        """
        self.brain.i = int(self.brain.shape[self.brain.section] / 2)
        self.widget_slider.maximum = self.brain.shape[self.brain.section] - 1
        self.widget_slider.slider.setMaximum(self.brain.shape[self.brain.section] - 1)
        self.win.refresh_image()

    def update0(self):
        """ Sets the view along axis 0

        This affects both labels and image data.
        This function is called by the first button.
        """
        self.brain.section = 0
        self.__update_section_helper()

    def update1(self):
        """ Sets the view along axis 1

        This affects both labels and image data.
        This function is called by the second button.
        """
        self.brain.section = 1
        self.__update_section_helper()

    def update2(self):
        """ Sets the view along axis 2

        This affects both labels and image data.
        This function is called by the third button.
        """
        self.brain.section = 2
        self.__update_section_helper()

    def extract(self):
        """ Performs brain extraction using the DeepBrain neural network

        This extraction produces a probability mask.
        At the moment it is hard coded such that we keep voxels with probability larger than a half.
        If the brain has already been extracted it loads a previous version.
        """
        if self.extracted:
            return 0
        elif len(self.only_brain) == 0:
            ext = Extractor()
            prob = ext.run(self.brain.data)
            print("EXTRACTION DONE")
            mask2 = np.where(prob > 0.5, 1, 0)
            self.only_brain = self.brain.data * mask2

        self.brain.data = self.only_brain
        self.win.refresh_image()
        self.extracted = True

    def normalize(self):
        """
        Method that returns an intensity-normalized image using the zero/mean unit stdev method
        To be edited
        """
        if self.normalized:
            return 0
        else:
            pass

    def segment(self):
        """
        Method that returns a segmented brain
        To be edited
        """
        if self.segmented:
            return 0
        else:
            pass

    def overlay(self):
        """
        Method that overlays a segmented mask on top of the original brain
        To be edited
        """
        if self.overlaid:
            return 0
        else:
            pass

    def full_brain(self):
        """ Returns the image to the original brain + head image

        Returns the background image to the unextracted brain.
        Stores the extracted brain.
        """
        if self.extracted:
            self.brain.data = self.full_head
            self.extracted = False
        self.img.setImage(self.brain.current_data_slice)
