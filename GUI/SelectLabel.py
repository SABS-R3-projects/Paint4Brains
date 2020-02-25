import Segmenter
from BrainData import BrainData
from PyQt5.QtWidgets import QComboBox, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy


class SelectLabel(QWidget):

    def __init__(self, window, parent=None):
        super(SelectLabel, self).__init__(parent=parent)
        self.brain = window.brain
        self.window = window
        self.new_layout = QHBoxLayout(self)
        self.dropbox = QComboBox()
        space = QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.new_layout.addItem(space)
        self.new_layout.addWidget(self.dropbox)
        self.names = Segmenter.label_names
        for name in self.names[2:]:
            self.dropbox.addItem(name)
        self.dropbox.currentIndexChanged.connect(self.update_brain)

    @property
    def current_index(self):
        return self.dropbox.currentIndex() + 1

    @current_index.setter
    def current_index(self, i):
        self.dropbox.setCurrentIndex(i - 1)

    def update_brain(self):
        self.brain.current_label = self.current_index
        self.window.refresh_image()

    def update_box(self):
        self.current_index = self.brain.current_label



