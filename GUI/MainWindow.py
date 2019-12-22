from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QMessageBox
from MainWidget import MainWidget
import pyqtgraph as pg
import nibabel as nib
import numpy as np


class MainWindow(QMainWindow):
    """MainWindow class.
    Wraps MainWidget to allow a Menu
    """
    def __init__(self, file, parent=None):
        """Initialises the Main Window
        Basically calls the MainWidget class which contains the bulk of the gui and enables the use of menus.
        Because of this most of this class is dedicated to defining menu entries and actions to be added to these entries
        Another thing it does is load the nib files from a string containing the path
        """
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
        self.setWindowTitle("Paint4Brains")

        # Making a menu
        self.statusBar()
        menu_bar = self.menuBar()
        self.file = menu_bar.addMenu("File")
        self.edit = menu_bar.addMenu("Edit")
        self.view_menu = menu_bar.addMenu("View")
        self.tools = menu_bar.addMenu("Tools")

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

        # Predefined actions that usually appear when you right click. Recycling one that resets the view here.
        viewBoxActionsList = self.main_widget.view.menu.actions()

        resetViewAction = viewBoxActionsList[0]
        resetViewAction.setText("Reset View")
        resetViewAction.setShortcut('Ctrl+V')
        self.view_menu.addAction(resetViewAction)

        for i in range(1, len(viewBoxActionsList)):
            ViewActions = viewBoxActionsList[i]
            self.view_menu.addAction(ViewActions)

        nodrawAction = QAction('Deactivate drawing', self)
        nodrawAction.setShortcut('Ctrl+D')
        nodrawAction.setStatusTip('Deactivate drawing')
        nodrawAction.triggered.connect(self.main_widget.unsetDrawKernel)
        self.edit.addAction(nodrawAction)

        extractAction = QAction('Extract Brain', self)
        extractAction.setShortcut('Ctrl+E')
        extractAction.setStatusTip('Extract Brain')
        extractAction.triggered.connect(self.main_widget.extract)
        self.tools.addAction(extractAction)

        unextractAction = QAction('See Full Brain', self)
        unextractAction.setShortcut('Ctrl+U')
        unextractAction.setStatusTip('See Full Brain')
        unextractAction.triggered.connect(self.main_widget.full_brain)
        self.tools.addAction(unextractAction)


    def load_initial(self):
        """ Loads the "base" brain
        The pre-segmentation scan has to be uploaded before the gui is initialised. This can be done either through the
        command line beforehand (this can be set in pycharm too) or through a window that appears on start (gets annoying).
        If you try to open it with nothing it complains and gives you an error message.
        """
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
        data = nib.as_closest_canonical(nib.load(self.data_filename))
        return data.get_fdata()

    def load(self):
        """ Loads some labelled data
        Opens a loading window through which you can select what label data file to load. Once a file is uploaded
        it automatically sets the app to drawing mode
        """
        self.label_filename = pg.QtGui.QFileDialog.getOpenFileName(self, "Load labeled data", "Please select the desired label data", "Nii Files (*.nii)")
        if isinstance(self.label_filename, tuple):
            self.label_filename = self.label_filename[0]  # Qt4/5 API difference
        if self.label_filename == '':
            return
        self.label_data = nib.as_closest_canonical(nib.load(self.label_filename))
        self.main_widget.load_label_data(np.flip(self.label_data.get_data().transpose()))

    def save(self):
        """ Saves the edited labelled data into a new file
        Saves edits into a new .nii file. Opens a window in which you can type the name of the new file you are saving.
        It still does not copy the headers (something to do)
        """
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
