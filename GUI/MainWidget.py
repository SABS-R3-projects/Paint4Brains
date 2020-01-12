from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QMainWindow, QAction, qApp, QLabel
import numpy as np
from Slider import Slider
from PlaneSelectionButtons import PlaneSelectionButtons
from BrainData import BrainData
from ModViewBox import ModViewBox
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from deepbrain import Extractor
import nibabel as nb

# Here I define the different type of paint brushes with which you can edit the image.
cross = np.array([
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]).astype(np.int8)

dot = np.array([[1]]).astype(np.int8)

rubber = np.array([[-1]]).astype(np.int8)


class MainWidget(QWidget):
    def __init__(self, brain, parent=None):
        super(MainWidget, self).__init__(parent=parent)

        # Inputting data
        self.brain = brain

        # Initialising some memory used by functions
        self.full_head = self.brain.data.copy()
        self.only_brain = []
        self.normalized = 0
        self.extracted = False
        self.segmented = False
        self.overlaid = False

        # Creating viewing box to see data
        self.win = pg.GraphicsView()
        self.view = ModViewBox()
        self.win.setCentralItem(self.view)

        # Making Images out of data
        self.over_img = pg.ImageItem(self.brain.current_label_data_slice, autoDownSmaple=False, opacity=0.3,
                                     compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.img = pg.ImageItem(self.brain.current_data_slice, autoDownsample=False,
                                compositionMode=QtGui.QPainter.CompositionMode_SourceOver)

        # Colouring the labelled data
        lut = np.array([[0, 0, 0, 0], [20, 235, 150, 255]])
        self.over_img.setLookupTable(lut)
        self.over_img.setLevels([0, 1])

        # Adding the images to the viewing box and setting it to drawing mode (if there is labeled data)
        self.view.addItem(self.img)
        self.view.addItem(self.over_img)
        if self.brain.label_filename is not None:
            self.enable_drawing()

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
        mouse_x = int(self.img.mapFromScene(pos).x())
        mouse_y = int(self.img.mapFromScene(pos).y())
        self.position.setText(str(self.brain.position_as_voxel(mouse_x, mouse_y)))

    def update_after_slider(self):
        """ Updates the viewed image after moving the slider.

        Updates the displayed slice depending on the new value of the slider.
        It does this for both the labels and image data.
        """
        self.brain.i = self.widget_slider.x
        self.img.setImage(self.brain.current_data_slice)
        self.over_img.setImage(self.brain.current_label_data_slice, autoLevels=False)

    def __update_section_helper(self):
        """ Helper function used to ensure that everything runs smoothly after the view axis is changed.

        Ensures that the viewed slice exists;
        Sets the slider limits to sensible values;
        Updates the view of label and image data.
        """
        self.brain.i = int(self.brain.shape[self.brain.section] / 2)
        self.widget_slider.maximum = self.brain.shape[self.brain.section] - 1
        self.widget_slider.slider.setMaximum(self.brain.shape[self.brain.section] - 1)
        self.img.setImage(self.brain.current_data_slice)
        self.over_img.setImage(self.brain.current_label_data_slice, autoLevels=False)

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
        self.img.setImage(self.brain.current_data_slice)
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

    def enable_drawing(self):
        """ Activates drawing mode

        The default pen is a voxel in size.
        """
        self.over_img.setDrawKernel(dot, mask=dot, center=(0, 0), mode='add')
        self.view.drawing = True

    def disable_drawing(self):
        """ Deactivates drawing mode

        It does this by deactivating the drawing kernel and
        setting the value of the drawing parameter in the modified view box to False.
        """
        if self.view.drawing:
            self.over_img.drawKernel = None
            self.view.drawing = False
            self.view.state["mouseMode"] = 3
        else:
            self.enable_drawing()

    def edit_button1(self):
        """ Sets the drawing mode to DOT

        This is basically a square of one voxel in size with value one.
        For all the editing buttons the matrix used to edit is defined at the top of the file
        """
        if self.view.drawing:
            self.over_img.setDrawKernel(dot, mask=dot, center=(0, 0), mode='add')

    def edit_button2(self):
        """ Sets the drawing mode to RUBBER

        Similar to DOT but removes the label from voxels .
        """
        if self.view.drawing:
            self.over_img.setDrawKernel(rubber, mask=rubber, center=(0, 0), mode='add')

    def edit_button3(self):
        """ Sets the drawing mode to SQUARE

        This sets the paintbrush to a cross of 3x3 voxels in size.
        """
        if self.view.drawing:
            self.over_img.setDrawKernel(cross, mask=cross, center=(1, 1), mode='add')
