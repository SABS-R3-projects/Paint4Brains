from pyqtgraph import ImageItem, GraphicsView
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QLabel
from PyQt5 import QtGui
from ModViewBox import ModViewBox


class MultipleViews(QWidget):
    def __init__(self, mainviewer, parent=None):
        super(MultipleViews, self).__init__(parent=parent)

        self.mainview = mainviewer
        self.brain = mainviewer.brain

        self.layout = QHBoxLayout(self)

        self.win1 = GraphicsView()
        self.view1 = ModViewBox()
        self.win1.setCentralItem(self.view1)

        # Making Images out of data
        self.brain.section = (self.brain.section - 1) % 3
        self.brain_img1 = ImageItem(self.brain.current_data_slice, autoDownsample=False,
                                    compositionMode=QtGui.QPainter.CompositionMode_SourceOver)
        self.label_img1 = ImageItem(self.brain.current_label_data_slice, autoDownSmaple=False, opacity=1,
                                    compositionMode=QtGui.QPainter.CompositionMode_Plus)
        self.brain.section = (self.brain.section + 1) % 3

        self.view1.addItem(self.brain_img1)
        self.view1.addItem(self.label_img1)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        print(self.sizeHint())
        self.layout.addWidget(self.win1)
