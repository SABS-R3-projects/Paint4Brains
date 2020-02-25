import numpy as np
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox
from PyQt5.QtCore import QRunnable, QThreadPool, QThread
from PyQt5.QtGui import QIcon, QFileDialog, QPushButton


class SegmentThread(QThread):
    '''
    Worker Thread.
    '''

    def __init__(self, window, device):
        super(SegmentThread, self).__init__()
        # Storing constructor arguments to re-use for processing
        self.device = device
        self.window = window
        self.brain = self.window.brain

    def run(self):
        self.brain.segment(self.device)
        self.window.enable_drawing()
        self.window.update_colormap()
        self.window.view_back_labels()