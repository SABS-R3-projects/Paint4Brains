"""GUI Main Window

This file contains all the relevant functions for defining and operating Paint4Brains' main window.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.MainWindow import MainWindow
        window = MainWindow(parameters)

"""

import numpy as np
import torch
import os
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QComboBox, QToolBar, QSizePolicy, QFileDialog, QPushButton, QDockWidget
from PyQt5.QtCore import QRunnable, QThreadPool, QThread, Qt, QSize
from PyQt5.QtGui import QIcon
from Paint4Brains.BrainData import BrainData
from Paint4Brains.GUI.MainWidget import MainWidget
from Paint4Brains.GUI.SegmentManager import SegmentThread, SegmentManager
from Paint4Brains.GUI.OptionalSliders import OptionalSliders
from Paint4Brains.GUI.MultipleViews import MultipleViews
from Paint4Brains.GUI.NormalizationWidget import NormalizationWidget
from Paint4Brains.GUI.HistogramWidget import HistogramWidget
######################
from pyqtgraph.dockarea import *
import pyqtgraph as pg
######################

class MainWindow(QMainWindow):
    """MainWindow class for Paint4Brains.

    This class contains the implementation of a series of functions required for the Main Windows of the Paint4Brains GUI.
    Wraps MainWidget to allow a Menu.
    To operate, the constructor class calls the MainWidget class which contains the bulk of the gui and enables the use of menus.
    Because of this most of this class is dedicated to defining menu entries and actions to be added to these entries
    Another thing it does is load the nib files from a string containing the path.

    Args:
        file (str): Path leading to the location of the brain data file.
        label_file (str): Path to the location of the labeled data file.
    """

    def __init__(self, file, label_file=None):

        super(MainWindow, self).__init__()

        if file is None:
            file = self.load_initial()

        self.brain = BrainData(file, label_file)
        self.main_widget = MainWidget(self.brain, self)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("Paint4Brains")
        ######################
        # w4 = pg.PlotWidget(title="Dock 4 plot")
        # w4.plot(np.random.normal(size=100))
        # dockWidget = QDockWidget('Dock', self)
        # dockWidget.setWidget(w4)
        # self.addDockWidget(Qt.RightDockWidgetArea, dockWidget)
        #####################


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

        oldButtonsAction = QAction('Single View Mode', self)
        oldButtonsAction.setStatusTip('Sets layout to single window mode')
        oldButtonsAction.triggered.connect(
            self.main_widget.revert_to_old_buttons)

        viewToolbarAction = QAction("Editting Toolbar", self)
        viewToolbarAction.setStatusTip("View Editting Toolbar")
        viewToolbarAction.triggered.connect(self.view_edit_tools)

        for i in [0]:  # range(1, len(viewBoxActionsList)):
            ViewActions = viewBoxActionsList[i]
            self.view_menu.addAction(ViewActions)

        self.view_menu.addSeparator()
        self.view_menu.addAction(oldButtonsAction)
        self.view_menu.addSeparator()
        self.view_menu.addAction(viewToolbarAction)

        viewVisualizationAction = QAction("Visualization Toolbar", self)
        viewVisualizationAction.setStatusTip("View Visualization Toolbar")
        viewVisualizationAction.triggered.connect(
            self.view_visualization_tools)
        self.view_menu.addAction(viewVisualizationAction)

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

        undoAction = QAction('Undo', self)
        undoAction.setShortcut('Ctrl+Z')
        undoAction.setStatusTip('Undo previous edit')
        undoAction.triggered.connect(self.main_widget.win.undo_previous_edit)
        self.edit.addAction(undoAction)

        undoAction = QAction('Redo', self)
        undoAction.setShortcut('Ctrl+Shift+Z')
        undoAction.setStatusTip('Revert to previous edit')
        undoAction.triggered.connect(self.main_widget.win.redo_previous_edit)
        self.edit.addAction(undoAction)

        # Creating the Ajust Intensity option under Tools and connecting it to the Intensity Adjustment widget
        #normalizeAction = QAction('Adjust Intensity', self)
        #normalizeAction.setShortcut('Ctrl+I')
        #normalizeAction.setStatusTip('Normalize Image Intensity')
        #normalizeAction.triggered.connect(self.view_intensity)
        #normalizeAction.triggered.connect(self.main_widget.normalize_intensity)
        #self.tools.addAction(normalizeAction)

        #######################################################################
        #Itai Working Adding Histogram
        histogramAction = QAction('Intensity Histogram', self)
        histogramAction.setShortcut('Ctrl+H')
        histogramAction.setStatusTip('View Intensity Histogram')
        histogramAction.triggered.connect(self.view_histogram)
        histogramAction.triggered.connect(self.main_widget.normalize_intensity)
        self.tools.addAction(histogramAction)

        #############################################################################
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

        segmentAction = QAction('Segment Brain', self)
        segmentAction.setShortcut('Ctrl+W')
        segmentAction.setStatusTip('Segment Brain')
        segmentAction.triggered.connect(self.segment)
        self.tools.addAction(segmentAction)

        # Editing tools as a toolbar
        current_directory = os.path.dirname(os.path.realpath(__file__))

        pen = QAction(QIcon(current_directory + "/images/pen.png"),
                      "Pencil: Draw Pixels", self)
        pen.triggered.connect(self.main_widget.win.edit_button1)

        rubber = QAction(QIcon(current_directory + "/images/eraser.png"),
                         "Eraser: Remove Drawn Pixels", self)
        rubber.triggered.connect(self.main_widget.win.edit_button2)

        cross = QAction(QIcon(current_directory + "/images/cross.png"),
                        "Brush: Draw Multiple Pixels", self)
        cross.triggered.connect(self.main_widget.win.edit_button3)

        bonus = QAction(QIcon(current_directory + "/images/star.png"),
                        "Custom: Make Your Own Brush", self)
        bonus.triggered.connect(self.main_widget.win.bonus_brush)

        left = QAction(QIcon(current_directory + "/images/left.png"),
                       "Previous Label: Go To Previously Selected Label", self)
        left.triggered.connect(self.main_widget.win.previous_label)

        label = QAction(QIcon(current_directory + "/images/label.png"),
                        "Select Label: Select Individual Label", self)
        label.triggered.connect(self.main_widget.win.select_label)

        right = QAction(QIcon(current_directory + "/images/right.png"),
                        "Next Label: Go To The Next Label", self)
        right.triggered.connect(self.main_widget.win.next_label)

        self.edit_toolbar = self.addToolBar("Editting Tools")
        self.edit_toolbar.setIconSize(QSize(40, 40))
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addAction(pen)
        self.edit_toolbar.addAction(cross)
        self.edit_toolbar.addAction(rubber)
        self.edit_toolbar.addAction(bonus)
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addAction(left)
        self.edit_toolbar.addAction(label)
        self.edit_toolbar.addAction(right)
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addSeparator()
        self.edit_toolbar.addWidget(self.main_widget.win.dropbox)
        self.edit_toolbar.setVisible(False)

        self.optional_sliders = QToolBar()
        self.addToolBar(Qt.RightToolBarArea, self.optional_sliders)
        self.optional_sliders.addWidget(OptionalSliders(self.main_widget.win))
        self.optional_sliders.setVisible(False)

        # Making the Intensity Normalization Tab invisible as long as Adjust Intensity has not yet been clicked
        self.norm_widget = NormalizationWidget(self.main_widget.win)
        self.intensity_toolbar = QToolBar()
        self.addToolBar(Qt.RightToolBarArea, self.intensity_toolbar)
        self.intensity_toolbar.addWidget(self.norm_widget)
        self.intensity_toolbar.setVisible(False)

        # Making the Histogram Tab invisible as long as Intensity Histogram has not yet been clicked
        self.hist_widget = HistogramWidget(self.main_widget.win)
        #self.histogram_toolbar = QToolBar()
        #self.addToolBar(Qt.RightToolBarArea, self.histogram_toolbar)
        #self.histogram_toolbar.addWidget(self.hist_widget)
        self.hist_widget.setVisible(False)

    def load_initial(self):
        """Original brain loader 

        Loads the "base" brain.
        The pre-segmentation scan has to be uploaded before the gui is initialised!
        This can be done either through the command line beforehand (this can be set in pycharm too) or through a window that appears on start (gets annoying).
        If you try to open it with nothing it complains and gives you an error message.

        Raises:
            Error: Failed to load!
        """
        self.data_filename = QFileDialog.getOpenFileName(self, "Load brain MRI",
                                                         "Please select full MRI scan", "Nii Files (*.nii *.nii.gz)")
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
        """Labelled data loader.

        This function loads labelled data.
        Opens a loading window through which you can select what label data file to load. 
        Once a file is uploaded it automatically sets the app to drawing mode
        """
        self.label_filename = QFileDialog.getOpenFileName(self, "Load labeled data",
                                                          "Please select the desired label data",
                                                          "Nii Files (*.nii *.nii.gz)")
        if isinstance(self.label_filename, tuple):
            # Qt4/5 API difference
            self.label_filename = self.label_filename[0]
        if self.label_filename == '':
            return
        self.brain.load_label_data(self.label_filename)
        self.main_widget.win.enable_drawing()
        self.main_widget.win.update_colormap()
        self.main_widget.win.view_back_labels()

    def save_as(self):
        """Labelled data saver with a new name

        This function saves the edited labelled data into a new file
        Saves edits into a new .nii file. Opens a window in which you can type the name of the new file you are saving.
        It still does not copy the headers (something to do)
        """
        old_name = self.brain.label_filename
        if old_name is None:
            old_name = "New_label_data"
        else:
            old_name = "Modified_" + old_name
        saving_filename = QFileDialog.getSaveFileName(
            self, "Save Image", old_name, "Nii Files (*.nii)")
        self.brain.save_label_data(saving_filename)

    def save(self):
        """Labelled data saver

        Saves the edited labelled data into a previously saved file
        Saves edits into a new .nii file. If no file has been saved before it reverts to save_as
        It still does not copy the headers (something to do)
        """
        if self.brain.saving_filename is None:
            self.save_as()
        else:
            self.brain.save_label_data(self.brain.saving_filename)

    def new(self):
        """Create new label

        If there are no other labels this is equivalent to enable drawing. 
        If there are other labels, this adds a new one and sets it to be the label that is being currently edited.
        """
        if np.sum(self.brain.label_data) == 0 and np.sum(self.brain.other_labels_data) == 0:
            self.main_widget.win.enable_drawing()
        else:
            self.brain.current_label = int(
                np.max(self.brain.different_labels)) + 1
            self.main_widget.win.refresh_image()
            self.main_widget.win.update_colormap()

    def view_edit_tools(self):
        """Toggle editing toolbar

        Switch the toolbar with editing buttons to visible or invisible
        Makes it the opposite of what it was previously
        """
        switch = not self.edit_toolbar.isVisible()
        self.edit_toolbar.setVisible(switch)

    def view_visualization_tools(self):
        """Toggle visualization toolbar

        Switch the toolbar with editing buttons to visible or invisible
        Makes it the opposite of what it was previously
        """
        switch = not self.optional_sliders.isVisible()
        self.optional_sliders.setVisible(switch)

    def view_intensity(self):
        """Toggle intensity widget

        Method that makes the intensity adjustment widget visible after the
        Adjust Intensity button under Tools has been clicked
        """
        switch = not self.intensity_toolbar.isVisible()
        self.intensity_toolbar.setVisible(switch)

    ###############################################################
    def view_histogram(self):
        switch = not self.hist_widget.isVisible()
        self.hist_widget.setVisible(switch)
    ##############################################################

    def segment(self):
        """Call the segmentation function

        Method that returns a segmented brain
        This funtion calls the brainSegmentation function in BrainData, which transforms (pre-processes) the brain file and then calls QuickNAT for running the file.
        """
        SegmentManager(self)
