import numpy as np
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox
from PyQt5.QtCore import QThreadPool, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QFileDialog, QPushButton
import torch


class SegmentThread(QThread):
    '''
    Worker Thread.
    '''
    start_signal = pyqtSignal()

    def __init__(self, window, device):
        super(SegmentThread, self).__init__()
        # Storing constructor arguments to re-use for processing
        self.device = device
        self.window = window
        self.brain = self.window.brain

    def run(self):
        self.start_signal.emit()
        print("Before")
        self.terminate()
        print("After")
        # self.brain.segment(self.device)
        self.window.enable_drawing()
        self.window.update_colormap()
        self.window.view_back_labels()
        self.terminate()


class SegmentMessageBox(QMessageBox):
    def __init__(self, parent):
        super(SegmentMessageBox, self).__init__(parent=parent)
        self.device = "None"
        self.parent = parent
        self.setWindowTitle("Select Hardware Type")
        self.setText("What type of processor would you like to use?")
        self.setInformativeText(
            "Running segmentation on a CPU takes around 2 hours. Running it on a GPU will take around 30 seconds.")
        self.setIcon(QMessageBox.Question)
        self.setDetailedText(
            "To perform the segmentation, Paint4Brain uses a convolutional neural network. This performs a lot faster on GPUs.\nIf you do not own a GPU, segmentation can also be run on a Google Colab GPU using the following link:\nhttps://tinyurl.com/Paint4Brains")

        self.addButton(QPushButton('CANCEL'), QMessageBox.RejectRole)
        self.addButton(QPushButton('GPU'), QMessageBox.AcceptRole)
        self.addButton(QPushButton('CPU'), QMessageBox.AcceptRole)

        self.setDefaultButton(QPushButton('CPU'))
        self.buttonClicked.connect(self.popup_button)

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
        cuda_available = torch.cuda.is_available()
        if device != "None" and (cuda_available or device != "cuda"):
            self.thread = SegmentThread(self.parent.main_widget.win, device)
            self.thread.start_signal.connect(self.started_message)
            self.thread.start()

    @pyqtSlot()
    def started_message(self):
        print("GOT HERE")
        msg = QMessageBox()
        msg.setText("Segmentation is running")
        msg.exec()
