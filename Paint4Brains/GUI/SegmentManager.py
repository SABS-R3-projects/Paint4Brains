import numpy as np
from PyQt5.QtWidgets import QMessageBox, QErrorMessage
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QIcon, QPushButton
from Paint4Brains.GUI.ProgressBar import ProgressBar


class SegmentThread(QThread):
    '''
    Worker Thread.
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
        self.start_signal.emit()
        try:
            self.brain.segment(self.device)
        except Exception as e:
            text = str(e)
            self.error_signal.emit(text)
        else:
            self.end_signal.emit()


class SegmentManager(QObject):
    def __init__(self, parent):
        super(SegmentManager, self).__init__(parent=parent)
        self.device = "None"
        self.parent = parent
        self.brain = self.parent.brain
        self.start_msg = ProgressBar(self)
        self.thread = SegmentThread(self.brain, self.device)
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
            self.thread.start_signal.connect(self.started_message)
            self.thread.end_signal.connect(self.finished_message)
            self.thread.error_signal.connect(self.error_message)
            self.thread.device = device
            self.thread.start()

    @pyqtSlot()
    def started_message(self):
        text = "Segmentation is now running."
        self.start_msg.label.setText(text)
        self.start_msg.setVisible(True)

    @pyqtSlot()
    def finished_message(self):
        msg = QMessageBox()
        msg.setText("Segmentation has finished successfully.")
        msg.exec()
        self.parent.main_widget.win.enable_drawing()
        self.parent.main_widget.win.update_colormap()
        self.parent.main_widget.win.view_back_labels()
        self.start_msg.close()

    @pyqtSlot(str)
    def error_message(self, error):
        self.start_msg.thread.terminate()
        self.start_msg.close()
        msg = QErrorMessage()
        text = "Error while running segmentation."
        msg.setWindowTitle(text)
        msg.showMessage("ERROR:\n" + error)
        msg.exec()

    def show_initial_message(self):
        initial_message = QMessageBox()
        initial_message.setWindowTitle("Select Hardware Type")
        initial_message.setText("What type of processor would you like to use?")
        initial_message.setInformativeText(
            "Running segmentation on a CPU takes around 3 hours. Running it on a GPU will take around 30 seconds.")
        initial_message.setIcon(QMessageBox.Question)
        initial_message.setDetailedText(
            "To perform the segmentation, Paint4Brain uses a convolutional neural network. This performs a lot faster on GPUs.\nIf you do not own a GPU, segmentation can also be run on a Google Colab GPU using the following link:\nhttps://tinyurl.com/Paint4Brains")

        initial_message.addButton(QPushButton('CANCEL'), QMessageBox.RejectRole)
        initial_message.addButton(QPushButton('GPU'), QMessageBox.AcceptRole)
        initial_message.addButton(QPushButton('CPU'), QMessageBox.AcceptRole)

        initial_message.setDefaultButton(QPushButton('CPU'))
        initial_message.buttonClicked.connect(self.popup_button)
        initial_message.exec()
