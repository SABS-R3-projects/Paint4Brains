"""Segmenter Manager Module

This file contains a collection of classes and functions which augment the segmentation operation.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.SegmentManager import SegmentThread, SegmentManager
        SegmentManager()

"""

from PyQt5.QtWidgets import QMessageBox, QErrorMessage
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QPushButton
from Paint4Brains.GUI.ProgressBar import ProgressBar


class SegmentThread(QThread):
    '''Segment Worker Thread

    In order to allow the operation of the software while segmentation is running, and prevent freezing on older hardware, the segmentation process is threaded.

    Attributes:
        start_signal (pyqtSignal): Signal marking the start of segmnetation
        end_signal (pyqtSignal): Signal marking the end of segmentation
        error_signal (pyqtSignal, str): String of any error raised during execution

    Args:
        window (class): ImageViewer class
        device (int/str): Device type used for training (int - GPU id, str- CPU)

    '''
    start_signal = pyqtSignal()
    end_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, brain, device):
        super(SegmentThread, self).__init__()
        # Storing constructor arguments to re-use for processing
        self.device = device
        self.brain = brain

    def run(self):
        """Run function

        Run function which, if receiving a run signal, starts the segmentation using a thread, or otherwise ends the thread or raises an error.
        """

        self.start_signal.emit()
        try:
            self.brain.segment(self.device)
        except Exception as e:
            text = str(e)
            self.error_signal.emit(text)
        else:
            self.end_signal.emit()


class SegmentManager(QObject):
    """SegmentManager class

    This is a class containing several useful functions which augment the segmentation process.

    Args:
        parent (class): Base or parent class

    """

    def __init__(self, parent):
        super(SegmentManager, self).__init__(parent=parent)
        self.device = "None"
        self.parent = parent
        self.brain = self.parent.brain
        self.start_msg = ProgressBar(self)
        self.thread = SegmentThread(self.brain, self.device)
        self.show_initial_message()

    def popup_button(self, i):
        """Popup button

        Opens a popup window, prompting the user to select the type of desired hardware for segmentation.

        Args:
            i (str): User input by pressing the button. 
        """
        if i.text() == 'CPU':
            self.device = 'cpu'
        elif i.text() == 'GPU':
            self.device = "cuda"
        else:
            self.device = "None"
        self.run_segmentation()
        print(type(i))

    def run_segmentation(self, device=None):
        """Run segmentation

        Function which runs the segmentation and assigns it to a thread.

        Args:
            device (int/str): Device type used for training (int - GPU id, str- CPU)
        """

        if device is None:
            device = self.device
        # Running segmentation in a separate thread, to prevent the GUI from crashing/freezing
        if device != "None":
            self.thread.start_signal.connect(self.started_message)
            self.thread.end_signal.connect(self.finished_message)
            self.thread.error_signal.connect(self.error_message)
            self.thread.device = device
            self.thread.start()

    @pyqtSlot()
    def started_message(self):
        """Start message prompt

        This function prompts the user with different messages based on the selected hardware configuration.
        """

        text = "Segmentation is now running."
        self.start_msg.label.setText(text)
        self.start_msg.setVisible(True)

    @pyqtSlot()
    def finished_message(self):
        """Finish prompt

        This function prompts the user that segmentation has ended.
        It also signals the ImageViewer to enable editing, display the labels and enable color editing.
        """
        msg = QMessageBox()
        msg.setText("Segmentation has finished successfully.")
        msg.exec()
        self.parent.main_widget.win.enable_drawing()
        self.parent.main_widget.win.update_colormap()
        self.parent.main_widget.win.view_back_labels()
        self.start_msg.close()

    @pyqtSlot(str)
    def error_message(self, error):
        """Error prompt

        This function produces an error message if one arises during segmentation.

        Args:
            error (pyqtSignal): Error signal generated during segmentation.
        """

        self.start_msg.thread.terminate()
        self.start_msg.close()
        msg = QErrorMessage()
        text = "Error while running segmentation."
        msg.setWindowTitle(text)
        msg.showMessage("ERROR:\n" + error)
        msg.exec()

    def show_initial_message(self):
        """Initial Message Prompts

        A series of initial messages displayed to the user in the Segmentation Popup Window
        """
        initial_message = QMessageBox()
        initial_message.setWindowTitle("Select Hardware Type")
        initial_message.setText(
            "What type of processor would you like to use?")
        initial_message.setInformativeText(
            "Running segmentation on a CPU takes around 3 hours. Running it on a GPU will take around 30 seconds.")
        initial_message.setIcon(QMessageBox.Question)
        initial_message.setDetailedText(
            "To perform the segmentation, Paint4Brain uses a convolutional neural network. This performs a lot faster on GPUs.\nIf you do not own a GPU, segmentation can also be run on a Google Colab GPU using the following link:\nhttps://tinyurl.com/Paint4Brains")

        initial_message.addButton(QPushButton(
            'CANCEL'), QMessageBox.RejectRole)
        initial_message.addButton(QPushButton('GPU'), QMessageBox.AcceptRole)
        initial_message.addButton(QPushButton('CPU'), QMessageBox.AcceptRole)

        initial_message.setDefaultButton(QPushButton('CPU'))
        initial_message.buttonClicked.connect(self.popup_button)
        initial_message.exec()
