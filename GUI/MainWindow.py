import numpy as np
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox
from PyQt5.QtGui import QIcon, QFileDialog
from MainWidget import MainWidget
from BrainData import BrainData


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
        newAction = QAction('New Label', self)
        newAction.setStatusTip('Create new label')
        newAction.triggered.connect(self.new)
        self.file.addAction(newAction)

        loadAction = QAction('Load Label', self)
        loadAction.setShortcut('Ctrl+L')
        loadAction.setStatusTip('Load Labels')
        loadAction.triggered.connect(self.load)
        self.file.addAction(loadAction)

        saveAction = QAction('Save', self)
        saveAction.setStatusTip('Save Labels')
        saveAction.triggered.connect(self.save)
        self.file.addAction(saveAction)

        saveAsAction = QAction('Save As', self)
        saveAsAction.setShortcut('Ctrl+S')
        saveAsAction.setStatusTip('Save labels to selected file')
        saveAsAction.triggered.connect(self.save_as)
        self.file.addAction(saveAsAction)

        # Predefined actions that usually appear when you right click. Recycling one that resets the view here.
        viewBoxActionsList = self.main_widget.win.view.menu.actions()

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
        self.view_menu.addSeparator()

        seeAllAction = QAction('All Labels', self)
        seeAllAction.setShortcut('Ctrl+A')
        seeAllAction.setStatusTip('Edit Next Segmented label')
        seeAllAction.triggered.connect(self.main_widget.win.view_back_labels)
        self.view_menu.addAction(seeAllAction)

        nextLabelAction = QAction('Next Label', self)
        nextLabelAction.setShortcut('Ctrl+N')
        nextLabelAction.setStatusTip('Edit Next Segmented label')
        nextLabelAction.triggered.connect(self.main_widget.win.next_label)
        self.edit.addAction(nextLabelAction)

        prevLabelAction = QAction('Previous Label', self)
        prevLabelAction.setShortcut('Ctrl+M')
        prevLabelAction.setStatusTip('Edit Previous Segmented label')
        prevLabelAction.triggered.connect(self.main_widget.win.previous_label)
        self.edit.addAction(prevLabelAction)

        selectLabelAction = QAction('Select Label', self)
        selectLabelAction.setStatusTip('Select Label to be edited')
        selectLabelAction.triggered.connect(self.main_widget.win.select_label)
        self.edit.addAction(selectLabelAction)
        self.edit.addSeparator()

        nodrawAction = QAction('Deactivate drawing', self)
        nodrawAction.setShortcut('Ctrl+D')
        nodrawAction.setStatusTip('Deactivate drawing')
        nodrawAction.triggered.connect(self.main_widget.win.disable_drawing)
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
        pen.triggered.connect(self.main_widget.win.edit_button1)

        rubber = QAction(QIcon("images/eraser.png"), "Rubber", self)
        rubber.triggered.connect(self.main_widget.win.edit_button2)

        cross = QAction(QIcon("images/cross.png"), "Cross", self)
        cross.triggered.connect(self.main_widget.win.edit_button3)

        left = QAction(QIcon("images/left.png"), "Previous Label", self)
        left.triggered.connect(self.main_widget.win.previous_label)

        label = QAction(QIcon("images/label.jpg"), "Select Label", self)
        label.triggered.connect(self.main_widget.win.select_label)

        right = QAction(QIcon("images/right.png"), "Next Label", self)
        right.triggered.connect(self.main_widget.win.next_label)

        self.edit_toolbar = self.addToolBar("Editting Tools")
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addAction(pen)
        self.edit_toolbar.addAction(rubber)
        self.edit_toolbar.addAction(cross)
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addAction(left)
        self.edit_toolbar.addAction(label)
        self.edit_toolbar.addAction(right)
        self.edit_toolbar.setVisible(False)

    def load_initial(self):
        """ Loads the "base" brain
        The pre-segmentation scan has to be uploaded before the gui is initialised. This can be done either through the
        command line beforehand (this can be set in pycharm too) or through a window that appears on start (gets annoying).
        If you try to open it with nothing it complains and gives you an error message.
        """
        self.data_filename = QFileDialog.getOpenFileName(self, "Load extracted brain",
                                                         "Please select full brain scan", "Nii Files (*.nii *.nii.gz)")
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
        self.label_filename = QFileDialog.getOpenFileName(self, "Load labeled data",
                                                          "Please select the desired label data",
                                                          "Nii Files (*.nii *.nii.gz)")
        if isinstance(self.label_filename, tuple):
            self.label_filename = self.label_filename[0]  # Qt4/5 API difference
        if self.label_filename == '':
            return
        self.brain.load_label_data(self.label_filename)
        self.main_widget.win.enable_drawing()
        self.main_widget.win.refresh_image()

    def save_as(self):
        """ Saves the edited labelled data into a new file
        Saves edits into a new .nii file. Opens a window in which you can type the name of the new file you are saving.
        It still does not copy the headers (something to do)
        """
        old_name = self.brain.label_filename
        if old_name is None:
            old_name = "New_label_data"
        else:
            old_name = "Modified_" + old_name
        saving_filename = QFileDialog.getSaveFileName(self, "Save Image..", old_name, "Nii Files (*.nii)")
        self.brain.save_label_data(saving_filename)

    def save(self):
        """ Saves the edited labelled data into a previously saved into file
        Saves edits into a new .nii file. If no file has been saved before it reverts to save_as
        It still does not copy the headers (something to do)
        """
        if self.brain.saving_filename is None:
            self.save_as()
        else:
            self.brain.save_label_data(self.brain.saving_filename)

    def new(self):
        if np.sum(self.brain.label_data) == 0:
            self.main_widget.win.enable_drawing()
        else:
            self.save_as()
            self.brain.label_data = np.zeros(self.brain.shape)

    def view_edit_tools(self):
        switch = not self.edit_toolbar.isVisible()
        self.edit_toolbar.setVisible(switch)
