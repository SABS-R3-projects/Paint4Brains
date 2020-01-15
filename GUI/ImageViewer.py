import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui
from pyqtgraph import ImageItem, GraphicsView
from ModViewBox import ModViewBox
from BrainData import BrainData
from matplotlib import cm

class ImageViewer(GraphicsView):
    def __init__(self, brain, parent=None):
        super(ImageViewer, self).__init__(parent=parent)

        # Inputting data
        self.brain = brain

        # Creating viewing box to see data
        self.view = ModViewBox()
        self.setCentralItem(self.view)

        # Making Images out of data
        self.over_img = ImageItem(self.brain.current_label_data_slice, autoDownSmaple=False, opacity=1,
                                  compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.mid_img = ImageItem(self.brain.current_other_labels_data_slice, autoDownSmaple=False, opacity=0.5,
                                 compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.img = ImageItem(self.brain.current_data_slice, autoDownsample=False,
                             compositionMode=QtGui.QPainter.CompositionMode_SourceOver)

        # Colouring the labelled data
        lut = np.array([[0, 0, 0, 0], [250, 0, 0, 255]])
        self.over_img.setLookupTable(lut)
        self.over_img.setLevels([0, 1])

        lut2 = [[0, 0, 0, 0], [140, 215, 239, 255], [38, 3, 196, 255], [68, 23, 193, 255], [119, 171, 229, 255], [73, 99, 86, 255], [92, 188, 223, 255], [69, 246, 9, 255], [27, 220, 151, 255], [161, 45, 249, 255], [118, 54, 69, 255], [212, 246, 124, 255], [87, 2, 201, 255], [116, 216, 46, 255], [17, 209, 23, 255], [109, 120, 234, 255], [66, 186, 85, 255], [248, 97, 234, 255], [16, 118, 161, 255], [167, 113, 206, 255], [82, 145, 154, 255], [23, 228, 47, 255], [29, 121, 164, 255], [84, 214, 219, 255], [85, 31, 45, 255], [53, 219, 24, 255], [100, 225, 31, 255], [250, 86, 132, 255], [18, 78, 84, 255], [80, 28, 185, 255], [215, 117, 51, 255], [61, 151, 58, 255], [40, 102, 175, 255]]
        #for _ in self.brain.different_labels:
        #    lut2.append([np.random.randint(0,255), np.random.randint(0,255), np.random.randint(0,255), 255])
        #print(lut2)

        # Apply the colormap
        self.mid_img.setLookupTable(np.array(lut2))

        # Adding the images to the viewing box and setting it to drawing mode (if there is labeled data)
        self.view.addItem(self.img)
        self.view.addItem(self.mid_img)
        self.view.addItem(self.over_img)

        if self.brain.label_filename is not None:
            self.enable_drawing()

    def refresh_image(self):
        self.img.setImage(self.brain.current_data_slice)
        self.mid_img.setImage(self.brain.current_other_labels_data_slice, autoLevels=False)
        self.over_img.setImage(self.brain.current_label_data_slice, autoLevels=False)

    def recenter(self):
        self.view.menu.actions()[0].trigger()

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
