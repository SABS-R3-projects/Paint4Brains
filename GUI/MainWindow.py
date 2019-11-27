from PyQt5.QtWidgets import QMainWindow, QAction, qApp
from MainWidget import MainWidget
import pyqtgraph as pg
import nibabel as nib
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self, data, labels, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.main_widget = MainWidget(data, self)
        self.setCentralWidget(self.main_widget)
        self.label_filename = None
        self.label_data = None

        # Making a menu
        self.statusBar()
        menu_bar = self.menuBar()
        self.file = menu_bar.addMenu("File")
        self.edit = menu_bar.addMenu("Edit")
        self.view_menu = menu_bar.addMenu("View")
        self.extra_menu = menu_bar.addMenu("This is intentionally very long to see what happens")

        # Actions in file bar (This enables shortcuts too)
        # Exit:
        exitAction = QAction('Load Labelled Data', self)
        exitAction.setShortcut('Ctrl+L')
        exitAction.setStatusTip('Load Labels')
        exitAction.triggered.connect(self.load)
        self.file.addAction(exitAction)

    def load(self):
        self.label_filename = pg.QtGui.QFileDialog.getOpenFileName(self, "Load labeled data", "Oh Hi there", "Nii Files (*.nii)")
        if isinstance(self.label_filename, tuple):
            self.label_filename = self.label_filename[0]  # Qt4/5 API difference
        if self.label_filename == '':
            return
        self.label_data = nib.load(self.label_filename)
        self.main_widget.load_label_data(np.flip(self.label_data.get_data().transpose()))
