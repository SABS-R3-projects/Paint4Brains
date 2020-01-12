import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui
from pyqtgraph import ImageItem, GraphicsView
from ModViewBox import ModViewBox
from BrainData import BrainData


class ImageViewer(GraphicsView):
    def __init__(self, brain, parent=None):
        super(ImageViewer, self).__init__(parent=parent)

        # Inputting data
        self.brain = brain

        # Creating viewing box to see data
        self.view = ModViewBox()
        self.setCentralItem(self.view)

        # Making Images out of data
        self.over_img = ImageItem(self.brain.current_label_data_slice, autoDownSmaple=False, opacity=0.3,
                                     compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.img = ImageItem(self.brain.current_data_slice, autoDownsample=False,
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

    def refresh_image(self):
        self.img.setImage(self.brain.current_data_slice)
        self.over_img.setImage(self.brain.current_label_data_slice, autoLevels=False)

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


cross = np.array([
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]).astype(np.int8)

dot = np.array([[1]]).astype(np.int8)

rubber = np.array([[-1]]).astype(np.int8)
