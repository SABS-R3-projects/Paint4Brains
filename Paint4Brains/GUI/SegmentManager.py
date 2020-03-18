import numpy as np
from PyQt5.QtWidgets import QMessageBox, QErrorMessage
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QIcon, QPushButton


class SegmentThread(QThread):
    '''
    Worker Thread.
    '''
    start_signal = pyqtSignal()
    end_signal = pyqtSignal()
    error_signal = pyqtSignal()

    def __init__(self, window, device):
        super(SegmentThread, self).__init__()
        # Storing constructor arguments to re-use for processing
        self.device = device
        self.window = window
        self.brain = self.window.brain

    def run(self):
        self.start_signal.emit()
        try:
            self.brain.segment(self.device)
            self.end_signal.emit()
        except:
            self.error_signal.emit()


class SegmentManager(QObject):
    def __init__(self, parent):
        super(SegmentManager, self).__init__(parent=parent)
        self.device = "None"
        self.parent = parent
        self.start_msg = QMessageBox()
        self.show_initial_message()

    def popup_button(self, i):
        if i.text() == 'CPU':
            self.device = 'cpu'
        elif i.text() == 'GPU':
            self.device = "cuda"
        else:
            self.device = "None"
        self.run_segmentation()

    def run_segmentation(self, device=None):
        if device is None:
            device = self.device
        # Running segmentation in a separate thread, to prevent the GUI from crashing/freezing
        if device != "None":
            self.thread = SegmentThread(self.parent.main_widget.win, device)
            self.thread.start_signal.connect(self.started_message)
            self.thread.end_signal.connect(self.finished_message)
            self.thread.error_signal.connect(self.error_message)
            self.thread.start()

    @pyqtSlot()
    def started_message(self):
        text = "Segmentation is now running.\n"
        if self.device == "cpu":
            text = text + "This may take up to 3 hours."
        elif self.device == "cuda":
            text = text + "This should be done in 20 seconds."
        self.start_msg.setText(text)
        self.start_msg.exec()

    @pyqtSlot()
    def finished_message(self):
        msg = QMessageBox()
        msg.setText("Segmentation has finished successfully.")
        msg.exec()
        self.parent.main_widget.win.enable_drawing()
        self.parent.main_widget.win.update_colormap()
        self.parent.main_widget.win.view_back_labels()

    @pyqtSlot()
    def error_message(self):
        self.start_msg.done(0)
        msg = QErrorMessage()
        text = "Error while running segmentation."
        if self.device == "cuda":
            text = text + "\nAre you sure you have a CUDA enabled GPU?"
        if self.device == "cpu":
            text = text + "\nPlease report this error."
        msg.showMessage(text)
        msg.exec()

    def show_initial_message(self):
        initial_message = QMessageBox()
        initial_message.setWindowTitle("Select Hardware Type")
        initial_message.setText("What type of processor would you like to use?")
        initial_message.setInformativeText(
            "Running segmentation on a CPU takes around 2 hours. Running it on a GPU will take around 30 seconds.")
        initial_message.setIcon(QMessageBox.Question)
        initial_message.setDetailedText(
            "To perform the segmentation, Paint4Brain uses a convolutional neural network. This performs a lot faster on GPUs.\nIf you do not own a GPU, segmentation can also be run on a Google Colab GPU using the following link:\nhttps://tinyurl.com/Paint4Brains")

        initial_message.addButton(QPushButton('CANCEL'), QMessageBox.RejectRole)
        initial_message.addButton(QPushButton('GPU'), QMessageBox.AcceptRole)
        initial_message.addButton(QPushButton('CPU'), QMessageBox.AcceptRole)

        initial_message.setDefaultButton(QPushButton('CPU'))
        initial_message.buttonClicked.connect(self.popup_button)
        initial_message.exec()
