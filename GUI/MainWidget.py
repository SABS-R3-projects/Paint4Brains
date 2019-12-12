from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QMainWindow, QAction, qApp
import numpy as np
from Slider import Slider
from PlaneSelectionButtons import PlaneSelectionButtons
from ModViewBox import ModViewBox
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

# Here I define the different type of paint brushes with which you can edit the image.
# For now it is constantly set to dot.
cross = np.array([
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]).astype(np.uint8)

dot = np.array([[1]]).astype(np.uint8)

rubber = np.array([[-1]]).astype(np.uint8)

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
        self.maxim = np.max(self.data)
        self.section = 0
        self.i = int(self.data.shape[self.section] / 2)

        # Making Images out of data
        self.over_img = pg.ImageItem(self.get_label_data(self.i), autoDownSmaple=False, opacity=0.3,
                                     compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.img = pg.ImageItem(self.get_data(self.i) / self.maxim, autoDownsample=False,
                                compositionMode=QtGui.QPainter.CompositionMode_SourceOver)
        self.buttons = PlaneSelectionButtons(self.update0, self.update1, self.update2)

        # Colouring the labelled data
        lut = np.array([[0, 0, 0, 0], [1, 245, 240, 255]])
        self.over_img.setLookupTable(lut)

        # Adding the images and setting it to drawing mode
        self.view.addItem(self.img)
        self.view.addItem(self.over_img)


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
        self.label_data = x
        self.over_img.setDrawKernel(dot, mask=cross, center=(0, 0), mode='add')
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
        self.over_img.setImage(self.get_label_data(self.i))

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
        self.over_img.setImage(self.get_label_data(self.i))

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

    def unsetDrawKernel(self):
        """ Deactivates drawing mode

        It does this by deactivating the drawing kernel and
        setting the value of the drawing parameter in the modified view box to False.
        """
        self.over_img.drawKernel = None
        self.view.drawing = False
