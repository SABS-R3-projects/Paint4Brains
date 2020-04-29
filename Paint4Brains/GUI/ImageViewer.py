"""GUI Image Viewer

This file contains a collection of functions relevant to defining the image and visualization properties of the GUI.

Attributes:
    cross (np.array): Array defining the shape of the kernel for the cross brush
    dot (np.array): Array defining the shape of the kernel for the dot brush
    rubber (np.array): Array defining the shape of the kernel for the rubber

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.ImageViewer import ImageViewer
        window = ImageViewer(parameters)

"""

from Paint4Brains.GUI.SelectLabel import SelectLabel
from Paint4Brains.GUI.ModViewBox import ModViewBox
from Paint4Brains.GUI.BonusBrush import BonusBrush
from Paint4Brains.BrainData import BrainData
from pyqtgraph import ImageItem, GraphicsView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QShortcut
import numpy as np

cross = np.array([
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]).astype(np.int8)

dot = np.array([[1]]).astype(np.int8)

rubber = np.array([[-1]]).astype(np.int8)


class ImageViewer(GraphicsView):

    """ImageViewer class for Paint4Brains.

    This class contains the implementation of a series of functions required for the GUI of the Paint4Brains project.

    Args:
        brain (class): BrainData class for Paint4Brains 
        parent (class): Base or parent class
    """

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
        self.mid_img = ImageItem(np.zeros(self.brain.current_other_labels_data_slice.shape), autoDownSmaple=False,
                                 opacity=0.7,
                                 compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.img = ImageItem(self.brain.current_data_slice, autoDownsample=False,
                             compositionMode=QtGui.QPainter.CompositionMode_SourceOver)

        # Colouring the labelled data
        lut = np.array([[0, 0, 0, 0], [250, 0, 0, 255]])
        self.over_img.setLookupTable(lut)
        self.over_img.setLevels([0, 1])

        # Maybe the visualization lecture was not that useless...
        self.colours = [[166, 206, 27],
                        [31, 120, 180],
                        [178, 223, 138],
                        [51, 160, 44],
                        [251, 154, 153],
                        [227, 26, 28],
                        [253, 191, 111],
                        [255, 127, 0],
                        [202, 178, 214],
                        [106, 61, 154],
                        [255, 255, 153],
                        [177, 89, 40]
                        # [0, 255, 0],  # Gree
                        # [255, 0, 0],  # Red
                        # [0, 0, 255],  #Blue
                        # [230, 138, 0]  #Orange


                        ]
        # self.colours = [[255, 0, 0],  #Red
        #                 [0, 0, 255],  #Blue
        #                 [230, 138, 0],  #Orange
        #                 [0, 255, 0],  #Green
        #                 [153, 51, 153],  #Purple
        #                 [179, 179, 0], #Yellow
        #                 [0, 204, 204],  # Cyan
        #                 [255, 102, 153], #Pink
        #                 [117, 36, 36], #Brown
        #                 [251, 154, 153],
        #                 [227, 26, 28],
        #                 [253, 191, 111],
        #                  [255, 127, 0],
        #                  [202, 178, 214],
        #                  [106, 61, 154],
        #                 [255, 255, 153],
        #                 [177, 89, 40]]

        self.update_colormap()

        # Adding the images to the viewing box and setting it to drawing mode (if there is labeled data)
        self.view.addItem(self.img)
        self.view.addItem(self.mid_img)
        self.view.addItem(self.over_img)

        self.select_mode = False
        self.see_all_labels = False

        if self.brain.label_filename is not None:
            self.enable_drawing()
            self.update_colormap()
            self.refresh_image()

        self.dropbox = SelectLabel(self)
        self.bonus = BonusBrush()
        self.bonus.buttn.clicked.connect(self.new_brush)

    def refresh_image(self):
        """Image Refresher

        Sets the images displayed by the Image viewer to the current data slices.
        It will only show all the labels if the self.see_all_labels parameters is True.
        """
        self.img.setImage(self.brain.current_data_slice)
        self.over_img.setImage(
            self.brain.current_label_data_slice, autoLevels=False)
        if self.see_all_labels:
            self.mid_img.setImage(
                self.brain.current_other_labels_data_slice, autoLevels=False)
        else:
            self.mid_img.setImage(
                np.zeros(self.brain.current_other_labels_data_slice.shape), autoLevels=False)

    def recenter(self):
        """Brain Recenter 

        Recenter the brain into the middle of the image viewer.
        The implementation may seem weird, but this is a predefined action by PyQt5.
        """
        self.view.menu.actions()[0].trigger()

    def update_colormap(self):
        """Label Colormap Update

        Updates the colormap to account for the current number of distinct labels.
        There are only 12 distinct colours (not including the "invisible" colour)
        """
        num = len(self.brain.different_labels) + 1
        self.mid_img.setLookupTable(
            np.array([[0, 0, 0]] + int(num / len(self.colours) + 1) * self.colours)[:num])
        self.mid_img.setLevels([0, np.max(self.brain.different_labels)])

    def enable_drawing(self):
        """Activates drawing mode

        The default pen is a voxel in size.
        """
        self.over_img.setDrawKernel(dot, mask=dot, center=(0, 0), mode='add')
        self.view.drawing = True

    def disable_drawing(self):
        """Deactivates drawing mode

        It does this by deactivating the drawing kernel and setting the value of the drawing parameter in the modified view box to False.
        """
        if self.view.drawing:
            self.over_img.drawKernel = None
            self.view.drawing = False
            self.view.state["mouseMode"] = 3
        else:
            self.enable_drawing()

    def edit_button1(self):
        """Sets the drawing mode to DOT

        This is basically a square of one voxel in size with value one.
        For all the editing buttons the matrix used to edit is defined at the top of the file
        """
        self.view.drawing = True
        self.over_img.setDrawKernel(dot, mask=dot, center=(0, 0), mode='add')

    def edit_button2(self):
        """Sets the drawing mode to RUBBER

        This is basically a square of one voxel in size with value one.
        For all the editing buttons the matrix used to edit is defined at the top of the file
        Removes the label from voxels.
        """
        self.view.drawing = True
        self.over_img.setDrawKernel(
            rubber, mask=rubber, center=(0, 0), mode='add')

    def edit_button3(self):
        """Sets the drawing mode to BRUSH (or square)

        This sets the paintbrush to a cross of 3x3 voxels in size.
        For all the editing buttons the matrix used to edit is defined at the top of the file
        """
        self.view.drawing = True
        self.over_img.setDrawKernel(
            cross, mask=cross, center=(1, 1), mode='add')

    def bonus_brush(self):
        self.enable_drawing()
        self.bonus.setVisible(True)

    def new_brush(self):
        self.enable_drawing()
        cent = len(self.bonus.pen)//2
        self.over_img.setDrawKernel(
            self.bonus.pen, mask=self.bonus.pen, center=(cent, cent), mode='add')

    def select_label(self):
        """Select label of interest

        Allows the user to select the location of the label to be edited next.
        Will only have effect if there are multiple labels from which to select
        The bulk of the implementation for this method is in the modified mouseReleasEevent method
        """
        if self.brain.multiple_labels:
            self.over_img.drawKernel = None
            self.select_mode = True

    def view_back_labels(self):
        """Toggle all/single label.

        Switch that determines whether all segmented areas are visible or just one.
        If see_all_labels was False, it makes all labels visible.
        If it was True it makes all labels except the one the user is currently editing invisible.
        """
        self.see_all_labels = not self.see_all_labels
        self.refresh_image()

    def next_label(self):
        """Label forward scroll

        Brings the next label in the list to be edited
        Lets you iterate through all existing labels
        """
        if self.brain.multiple_labels:
            new_index = np.where(self.brain.different_labels ==
                                 self.brain.current_label)[0][0] + 1
            if new_index < len(self.brain.different_labels):
                self.brain.current_label = self.brain.different_labels[new_index]
            else:
                self.brain.current_label = self.brain.different_labels[1]
            self.refresh_image()
            self.dropbox.update_box()

    def previous_label(self):
        """Label backward scroll

        Brings the previous label in the list to be edited
        Lets you iterate through all existing labels
        """
        if self.brain.multiple_labels:
            old_index = np.where(self.brain.different_labels ==
                                 self.brain.current_label)[0][0]
            if old_index != 1:
                self.brain.current_label = self.brain.different_labels[old_index - 1]
            else:
                self.brain.current_label = self.brain.different_labels[-1]
            self.refresh_image()
            self.dropbox.update_box()

    def undo_previous_edit(self):
        """Undo function

        This function reverts the previous user action and refreshes the image.
        """
        current = self.brain.current_edit
        if current > 1:
            self.brain.label_data = self.brain.edit_history[current - 2][0]
            self.brain.other_labels_data = self.brain.edit_history[current - 2][1]
            self.brain.current_edit = self.brain.current_edit - 1
            self.refresh_image()

    def redo_previous_edit(self):
        """Redo function

        This function re-does a previously reverted actions.
        """

        current = self.brain.current_edit
        if current < len(self.brain.edit_history):
            self.brain.label_data = self.brain.edit_history[current][0]
            self.brain.other_labels_data = self.brain.edit_history[current][1]
            self.brain.current_edit = self.brain.current_edit + 1
            self.refresh_image()

    def mouseReleaseEvent(self, ev):
        """Mouse event tracker

        This function keeps track of the actions performed by the mouse, while taking the selcted mode into account.
        If when select_mode is activated, the left button is released on a previously labeled area, then the pen is set to that label. Otherwise, everything should work as normal (the default)
        Now when you release the left button it assumes an edit has been made and stores it into the BrainData.

        Args:
            ev: signal emitted when user releases a mouse button.
        """
        if self.select_mode:
            if ev.button() == Qt.LeftButton:
                pos = ev.pos()
                mouse_x = int(self.img.mapFromScene(pos).x())
                mouse_y = int(self.img.mapFromScene(pos).y())
                location = self.brain.position_as_voxel(mouse_x, mouse_y)
                within = 0 < location[0] < self.brain.shape[0] and 0 < location[1] < self.brain.shape[1] and 0 < \
                    location[2] < self.brain.shape[2]
                if within:
                    label = self.brain.other_labels_data[location]
                    if label > 0:
                        self.brain.current_label = self.brain.other_labels_data[location]
                        self.select_mode = False
                        self.refresh_image()
                        self.enable_drawing()
                        self.dropbox.update_box()
        super(ImageViewer, self).mouseReleaseEvent(ev)
        if self.view.drawing and ev.button() == Qt.LeftButton:
            self.brain.store_edit()

    def wheelEvent(self, ev):
        """ Overwriting the wheel functionality.

        If you scroll it will move along slices.
        If you scroll while holding the Ctrl button, it will zoom in and out

        Args:
            ev: signal emitted when user releases scrolls the wheel.
        """

        if ev.modifiers() == Qt.ControlModifier:
            super(ImageViewer, self).wheelEvent(ev)
        else:
            if ev.angleDelta().y() > 0 and self.brain.i < self.brain.shape[self.brain.section] - 1:
                self.brain.i = self.brain.i + 1
                self.refresh_image()
            elif ev.angleDelta().y() < 0 < self.brain.i:
                self.brain.i = self.brain.i - 1
                self.refresh_image()
