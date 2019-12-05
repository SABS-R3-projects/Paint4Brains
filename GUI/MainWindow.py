from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QMessageBox, QUndoStack
from MainWidget import MainWidget
import pyqtgraph as pg
import nibabel as nib
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self, file, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.data_filename = file
        if file is None:
            data = self.load_initial()
        else:
            xim = nib.load(file)
            data = xim.get_fdata()
        self.label_filename = ""
        self.label_data = None

        self.main_widget = MainWidget(data, self)
        self.setCentralWidget(self.main_widget)

        # Making a menu
        self.statusBar()
        menu_bar = self.menuBar()
        self.file = menu_bar.addMenu("File")
        self.edit = menu_bar.addMenu("Edit")
        self.view_menu = menu_bar.addMenu("View")

        # Actions in file bar (This enables shortcuts too)
        # Exit:
        loadAction = QAction('Load Labelled Data', self)
        loadAction.setShortcut('Ctrl+L')
        loadAction.setStatusTip('Load Labels')
        loadAction.triggered.connect(self.load)
        self.file.addAction(loadAction)

        saveAction = QAction('Save Labelled Data', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Load Labels')
        saveAction.triggered.connect(self.save)
        self.file.addAction(saveAction)

        viewBoxActionsList = self.main_widget.view.menu.actions()

        resetViewAction = viewBoxActionsList[0]
        resetViewAction.setText("Reset View")
        resetViewAction.setShortcut('Ctrl+V')
        self.view_menu.addAction(resetViewAction)

        for i in range(1, len(viewBoxActionsList)):
            ViewActions = viewBoxActionsList[i]
            self.view_menu.addAction(ViewActions)

    def load_initial(self):
        self.data_filename = pg.QtGui.QFileDialog.getOpenFileName(self, "Load extracted brain", "Please select full brain scan", "Nii Files (*.nii)")
        if isinstance(self.data_filename, tuple):
            self.data_filename = self.data_filename[0]  # Qt4/5 API difference
        if self.data_filename == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Can not start without initial brain")
            msg.setInformativeText("Please load a brain image either via the command line or via the initial load window")
            msg.setWindowTitle("Error: Failed to load")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return #self.load_initial()
        data = nib.load(self.data_filename)
        return data.get_fdata()

    def load(self):
        self.label_filename = pg.QtGui.QFileDialog.getOpenFileName(self, "Load labeled data", "Please select the desired label data", "Nii Files (*.nii)")
        if isinstance(self.label_filename, tuple):
            self.label_filename = self.label_filename[0]  # Qt4/5 API difference
        if self.label_filename == '':
            return
        self.label_data = nib.load(self.label_filename)
        self.main_widget.load_label_data(np.flip(self.label_data.get_data().transpose()))

    def save(self):
        if self.label_filename == '':
            return
        saving_filename = pg.QtGui.QFileDialog.getSaveFileName(self, "Save Image..", "modified_" + self.label_filename, "Nii Files (*.nii)")
        if saving_filename[1] != "Nii Files (*.nii)":
            return
        elif (saving_filename[0])[-4:] != ".nii":
            saving_filename = saving_filename[0] + ".nii"
        else:
            saving_filename = saving_filename[0]

        image = nib.Nifti1Image(np.flip(self.main_widget.label_data).transpose(), np.eye(4))
        print(saving_filename)
        nib.save(image, saving_filename)
