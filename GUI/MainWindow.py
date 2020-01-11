from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QMessageBox
from PyQt5.QtGui import QIcon
from MainWidget import MainWidget
from BrainData import BrainData
import pyqtgraph as pg
import nibabel as nib
import numpy as np


class MainWindow(QMainWindow):
    """MainWindow class.
    Wraps MainWidget to allow a Menu
    """

    def __init__(self, file, label_file=None):
        """Initialises the Main Window
        Basically calls the MainWidget class which contains the bulk of the gui and enables the use of menus.
        Because of this most of this class is dedicated to defining menu entries and actions to be added to these entries
        Another thing it does is load the nib files from a string containing the path
        """
        super(MainWindow, self).__init__()

        if file is None:
            file = self.load_initial()

        self.brain = BrainData(file, label_file)
        self.main_widget = MainWidget(self.brain, self)

        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("Paint4Brains")

        # Making a menu
        menu_bar = self.menuBar()
        self.file = menu_bar.addMenu("File")
        self.edit = menu_bar.addMenu("Edit")
        self.view_menu = menu_bar.addMenu("View")
        self.tools = menu_bar.addMenu("Tools")
        self.help = menu_bar.addMenu("Help")

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
        resetViewAction.setText("Recenter View")
        resetViewAction.setShortcut('Ctrl+V')
        self.view_menu.addAction(resetViewAction)

        viewToolbarAction = QAction("Editting Toolbar", self)
        viewToolbarAction.setStatusTip("View Editting Toolbar")
        viewToolbarAction.triggered.connect(self.view_edit_tools)

        for i in [0]:  # range(1, len(viewBoxActionsList)):
            ViewActions = viewBoxActionsList[i]
            self.view_menu.addAction(ViewActions)

        self.view_menu.addSeparator()
        self.view_menu.addAction(viewToolbarAction)

        nodrawAction = QAction('Deactivate drawing', self)
        nodrawAction.setShortcut('Ctrl+D')
        nodrawAction.setStatusTip('Deactivate drawing')
        nodrawAction.triggered.connect(self.main_widget.disable_drawing)
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

        normalizeAction = QAction('Normalize Intensity', self)
        normalizeAction.setShortcut('Ctrl+N')
        normalizeAction.setStatusTip('Normalize Intensity')
        normalizeAction.triggered.connect(self.main_widget.normalize)
        self.tools.addAction(normalizeAction)

        segmentAction = QAction('Segment Brain', self)
        segmentAction.setShortcut('Ctrl+S')
        segmentAction.setStatusTip('Segment Brain')
        segmentAction.triggered.connect(self.main_widget.segment)
        self.tools.addAction(segmentAction)

        overlayAction = QAction('Brain-Segmentation Overlay', self)
        overlayAction.setShortcut('Ctrl+O')
        overlayAction.setStatusTip('Brain-Segmentation Overlay')
        overlayAction.triggered.connect(self.main_widget.overlay)
        self.tools.addAction(overlayAction)

        # Editing tools as a toolbar
        pen = QAction(QIcon("images/pen.jpeg"), "Pen", self)
        pen.triggered.connect(self.main_widget.edit_button1)

        rubber = QAction(QIcon("images/eraser.png"), "Rubber", self)
        rubber.triggered.connect(self.main_widget.edit_button2)

        cross = QAction(QIcon("images/cross.png"), "Cross", self)
        cross.triggered.connect(self.main_widget.edit_button3)

        self.edit_toolbar = self.addToolBar("Editting Tools")
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addAction(pen)
        self.edit_toolbar.addAction(rubber)
        self.edit_toolbar.addAction(cross)
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.setVisible(False)

    def load_initial(self):
        """ Loads the "base" brain
        The pre-segmentation scan has to be uploaded before the gui is initialised. This can be done either through the
        command line beforehand (this can be set in pycharm too) or through a window that appears on start (gets annoying).
        If you try to open it with nothing it complains and gives you an error message.
        """
        self.data_filename = pg.QtGui.QFileDialog.getOpenFileName(self, "Load extracted brain",
                                                                  "Please select full brain scan", "Nii Files (*.nii)")
        if isinstance(self.data_filename, tuple):
            self.data_filename = self.data_filename[0]  # Qt4/5 API difference
        if self.data_filename == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Can not start without initial brain")
            msg.setInformativeText(
                "Please load a brain image either via the command line or via the initial load window")
            msg.setWindowTitle("Error: Failed to load")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return  # self.load_initial()
        return self.data_filename

    def load(self):
        """ Loads some labelled data
        Opens a loading window through which you can select what label data file to load. Once a file is uploaded
        it automatically sets the app to drawing mode
        """
        self.label_filename = pg.QtGui.QFileDialog.getOpenFileName(self, "Load labeled data",
                                                                   "Please select the desired label data",
                                                                   "Nii Files (*.nii)")
        if isinstance(self.label_filename, tuple):
            self.label_filename = self.label_filename[0]  # Qt4/5 API difference
        if self.label_filename == '':
            return
        self.main_widget.brain.load_label_data(self.label_filename)
        self.main_widget.enable_drawing()

    def save(self):
        """ Saves the edited labelled data into a new file
        Saves edits into a new .nii file. Opens a window in which you can type the name of the new file you are saving.
        It still does not copy the headers (something to do)
        """
        if self.label_filename == '':
            return
        saving_filename = pg.QtGui.QFileDialog.getSaveFileName(self, "Save Image..", "modified_" + self.label_filename,
                                                               "Nii Files (*.nii)")
        if saving_filename[1] != "Nii Files (*.nii)":
            return
        elif (saving_filename[0])[-4:] != ".nii":
            saving_filename = saving_filename[0] + ".nii"
        else:
            saving_filename = saving_filename[0]

        image = nib.Nifti1Image(np.flip(self.main_widget.label_data).transpose(), np.eye(4))
        print(saving_filename)
        nib.save(image, saving_filename)

    def view_edit_tools(self):
        switch = not self.edit_toolbar.isVisible()
        self.edit_toolbar.setVisible(switch)
