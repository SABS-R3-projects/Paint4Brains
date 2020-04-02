from PyQt5.QtWidgets import QProgressBar, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject
import time


class ProgressBarThread(QThread):
    '''
    Worker Thread.
    '''
    update_values_signal = pyqtSignal()

    def __init__(self):
        super(ProgressBarThread, self).__init__()

    def run(self):
        while True:
            self.update_values_signal.emit()
            time.sleep(3)


class ProgressBar(QWidget):
    def __init__(self, segmenter):
        super(ProgressBar, self).__init__()

        self.segmenter = segmenter

        self.setWindowTitle("Segmentation in Progress")
        self.label = QLabel("Segmentation Started")
        self.progress = QProgressBar()

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress)

        self.thread = ProgressBarThread()
        self.thread.update_values_signal.connect(self.update_bar)
        self.thread.start()

    @pyqtSlot()
    def update_bar(self):
        self.progress.setValue(self.segmenter.completion)
        self.label.setText(self.segmenter.state)
