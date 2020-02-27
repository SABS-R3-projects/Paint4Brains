from pyqtgraph import ImageItem, GraphicsView, ViewBox, InfiniteLine
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QLabel
from PyQt5 import QtGui, QtCore
import numpy as np


class SideView(GraphicsView):
    def __init__(self, diff, parent=None):
        super(SideView, self).__init__(parent=parent)
        self.parent = parent
        self.brain = parent.brain
        self.diff = diff

        self.view1 = ViewBox()
        self.setCentralItem(self.view1)

        # Making Images out of data
        self.brain.section = (self.brain.section + self.diff) % 3
        self.i = int(self.brain.shape[self.brain.section] / 2)
        data_slice = self.brain.get_data_slice(self.i)
        self.brain_img1 = ImageItem(data_slice, autoDownsample=False,
                                    compositionMode=QtGui.QPainter.CompositionMode_SourceOver)
        self.brain.section = (self.brain.section - self.diff) % 3

        self.view1.addItem(self.brain_img1)
        self.view1.setAspectLocked(True)

        self.view1.setFixedHeight(250)
        self.view1.setFixedWidth(250)
        self.setMinimumHeight(250)

        self.vLine = InfiniteLine(angle=90, movable=False)
        self.hLine = InfiniteLine(angle=0, movable=False)
        self.vLine.setVisible(False)
        self.hLine.setVisible(False)
        self.view1.addItem(self.vLine, ignoreBounds=True)
        self.view1.addItem(self.hLine, ignoreBounds=True)

    def refresh_image(self):
        self.brain.section = (self.brain.section + self.diff) % 3
        data_slice = self.brain.get_data_slice(self.i)
        self.brain_img1.setImage(data_slice)
        self.brain.section = (self.brain.section - self.diff) % 3

    def refresh_all_images(self):
        self.parent.main_widget._update_section_helper()
        self.parent.win1.refresh_image()
        self.parent.win1.view1.menu.actions()[0].trigger()
        self.parent.win2.refresh_image()
        self.parent.win2.view1.menu.actions()[0].trigger()

    def mouseDoubleClickEvent(self, event):
        super(SideView, self).mouseDoubleClickEvent(event)
        self.brain.section = (self.brain.section + self.diff) % 3
        self.refresh_all_images()

    def set_i(self, position, out_of_box = False):
        section = (self.brain.section + self.diff) % 3
        if out_of_box:
            self.i = int(self.brain.shape[section]/2)
            self.vLine.setVisible(False)
            self.hLine.setVisible(False)
        else:
            i = position[section]
            self.i = np.clip(i, 0, self.brain.shape[section]-1)
            self.vLine.setVisible(True)
            self.hLine.setVisible(True)

            self.brain.section = (self.brain.section + self.diff) % 3
            x, y = self.brain.voxel_as_position(position[0], position[1], position[2])
            self.brain.section = (self.brain.section - self.diff) % 3
            self.vLine.setPos(x)
            self.hLine.setPos(y)
