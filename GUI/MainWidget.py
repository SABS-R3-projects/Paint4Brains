from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QMainWindow, QAction, qApp
import numpy as np
import os  # Itai added
from Slider import Slider
from PlaneSelectionButtons import PlaneSelectionButtons
from EditingButtons import EditingButtons
from ModViewBox import ModViewBox
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from deepbrain import Extractor
import nibabel as nb

# Here I define the different type of paint brushes with which you can edit the image.
# For now it is constantly set to dot.
cross = np.array([
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]).astype(np.int8)

dot = np.array([[1]]).astype(np.int8)

rubber = np.array([[-1]]).astype(np.int8)


class MainWidget(QWidget):
    def __init__(self, data, parent=None):
        super(MainWidget, self).__init__(parent=parent)
        # Creating a central widget to take everything in

        # Creating viewing box to see data
        self.win = pg.GraphicsView()
        self.view = ModViewBox()
        self.view.setAspectLocked(True)
        self.win.setCentralItem(self.view)

        # Inputting data
        self.data = np.flip(data.transpose())
        self.label_data = np.zeros(self.data.shape)
        self.full_head = self.data.copy()
        self.maxim = np.max(self.data)
        self.section = 0
        self.normalized = 0
        self.extracted = False
        self.segmented = False
        self.overlaid = False
        self.only_brain = []
        self.i = int(self.data.shape[self.section] / 2)

        # Making Images out of data
        self.over_img = pg.ImageItem(self.get_label_data(self.i), autoDownSmaple=False, opacity=0.3,
                                     compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.img = pg.ImageItem(self.get_data(self.i) / self.maxim, autoDownsample=False,
                                compositionMode=QtGui.QPainter.CompositionMode_SourceOver)
        self.buttons = PlaneSelectionButtons(self.update0, self.update1, self.update2)

        # Colouring the labelled data
        lut = np.array([[0, 0, 0, 0], [20, 235, 150, 255]])
        self.over_img.setLookupTable(lut)
        self.over_img.setLevels([0, 1])

        # Adding the images and setting it to drawing mode
        self.view.addItem(self.img)
        self.view.addItem(self.over_img)

        # Creating Editing Button
        editing_icon_list = ['images/pen.jpeg', 'images/eraser.png', 'images/cross.png']
        function_list = [self.edit_button1, self.edit_button2, self.edit_button3]
        self.editing_buttons = EditingButtons(function_list, editing_icon_list)

        # Creating a slider to go through image slices
        self.widget_slider = Slider(0, self.data.shape[self.section] - 1)
        self.widget_slider.slider.setMaximum(self.data.shape[self.section] - 1)
        self.widget_slider.slider.setValue(self.i)
        self.widget_slider.slider.valueChanged.connect(self.update_after_slider)

        # Arranging the layout
        self.horizontalLayout = QHBoxLayout()

        self.horizontalLayout.addWidget(self.buttons)
        self.horizontalLayout.addWidget(self.win)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.editing_buttons)
        spacerItem = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout.addSpacerItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.widget_slider)

    def get_data(self, i):
        """ Returns the 2-D slice at point i of the full MRI data (not labels).

        Depending on the desired view (self.section) it returns a different 2-D slice of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation
        """
        if self.section == 0:
            return self.data[i]
        elif self.section == 1:
            return np.flip(self.data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.data[:, :, i].transpose(), axis=1)

    def get_label_data(self, i):
        """ Returns the 2-D slice at point i of the labelled data.

        Depending on the desired view (self.section) it returns 2-D slice with respect to a different axis of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation
        """
        if self.section == 0:
            return self.label_data[i]
        elif self.section == 1:
            return np.flip(self.label_data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.label_data[:, :, i].transpose(), axis=1)

    def set_label_data(self, i, x):
        """ Sets the data at a certain slice i to the 2-D array x.

        Depending on the desired view (self.section) it sets a 2-D slice with respect to a different axis of the 3-D data
        This function is not currently used.
        """
        if self.section == 0:
            self.label_data[i] = x
        elif self.section == 1:
            self.label_data[:, i] = np.flip(x.transpose())
        elif self.section == 2:
            self.label_data[:, :, i] = np.flip(x.transpose(), axis=1)

    def load_label_data(self, x):
        """ Loads a given 3-D binary array (x) into the GUI.

        It then sets the GUI into drawing mode, so that the uploaded labeled data can be edited
        The paintbrush is hardcoded to a point for now
        """
        self.label_data = x.astype(np.int8)
        self.over_img.setDrawKernel(dot, mask=dot, center=(0, 0), mode='add')
        self.view.drawing = True

    def update_after_slider(self):
        """ Updates the viewed image after moving the slider.

        Updates the displayed slice depending on the new value of the slider.
        It does this for both the labels and image data.

        IMPORTANT: it ensures that the labelled data is binary (0 or 1) (np.clip)
        """
        self.label_data = np.clip(self.label_data, 0, 1)
        self.i = self.widget_slider.x
        self.img.setImage(self.get_data(self.i) / self.maxim)
        self.over_img.setImage(self.get_label_data(self.i), autoLevels=False)

    def update_section_helper(self):
        """ Helper function used to ensure that everything runs smoothly after the view axis is changed.

        Ensures that the viewed slice exists;
        Sets the slider limits to sensible values;
        Updates the view of label and image data.

        IMPORTANT: it ensures that the labelled data is binary (0 or 1) (np.clip)
        """
        self.label_data = np.clip(self.label_data, 0, 1)
        self.i = int(self.data.shape[self.section] / 2)
        self.widget_slider.maximum = self.data.shape[self.section] - 1
        self.widget_slider.slider.setMaximum(self.data.shape[self.section] - 1)
        self.img.setImage(self.get_data(self.i) / self.maxim)
        self.over_img.setImage(self.get_label_data(self.i), autoLevels=False)

    def update0(self):
        """ Sets the view along axis 0

        This affects both labels and image data.
        This function is called by the first button.
        """
        self.section = 0
        self.update_section_helper()

    def update1(self):
        """ Sets the view along axis 1

        This affects both labels and image data.
        This function is called by the second button.
        """
        self.section = 1
        self.update_section_helper()

    def update2(self):
        """ Sets the view along axis 2

        This affects both labels and image data.
        This function is called by the third button.
        """
        self.section = 2
        self.update_section_helper()

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
            prob = ext.run(self.data)
            print("EXTRACTION DONE")
            mask2 = np.where(prob > 0.5, 1, 0)
            self.only_brain = self.data * mask2

        self.data = self.only_brain
        self.img.setImage(self.get_data(self.i) / self.maxim)
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
            self.data = self.full_head
            self.extracted = False
        self.img.setImage(self.get_data(self.i) / self.maxim)

    def unsetDrawKernel(self):
        """ Deactivates drawing mode

        It does this by deactivating the drawing kernel and
        setting the value of the drawing parameter in the modified view box to False.
        """
        self.over_img.drawKernel = None
        self.view.drawing = False

    def edit_button1(self):
        """ Sets the drawing mode to DOT

        This is basically a square of one voxel in size with value one.
        For all the editing buttons the matrix used to edit is defined at the top of the file
        """
        if self.view.drawing:
            self.label_data = np.clip(self.label_data, 0, 1)
            self.over_img.setDrawKernel(dot, mask=dot, center=(0, 0), mode='add')
            self.label_data = np.clip(self.label_data, 0, 1)

    def edit_button2(self):
        """ Sets the drawing mode to RUBBER

        Similar to DOT but removes the label from voxels .
        """
        if self.view.drawing:
            self.label_data = np.clip(self.label_data, 0, 1)
            self.over_img.setDrawKernel(rubber, mask=rubber, center=(0, 0), mode='add')
            self.label_data = np.clip(self.label_data, 0, 1)

    def edit_button3(self):
        """ Sets the drawing mode to SQUARE

        This sets the paintbrush to a cross of 3x3 voxels in size.
        """
        if self.view.drawing:
            self.label_data = np.clip(self.label_data, 0, 1)
            self.over_img.setDrawKernel(cross, mask=cross, center=(1, 1), mode='add')
            self.label_data = np.clip(self.label_data, 0, 1)
