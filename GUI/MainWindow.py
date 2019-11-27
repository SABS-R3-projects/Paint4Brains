from PyQt5.QtWidgets import QMainWindow, QAction, qApp
from MainWidget import MainWidget


class MainWindow(QMainWindow):
    def __init__(self, data, labels, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.main_widget = MainWidget(data, labels, self)
        self.setCentralWidget(self.main_widget)

        # Making a menu
        self.statusBar()
        menu_bar = self.menuBar()
        self.file = menu_bar.addMenu("File")
        self.edit = menu_bar.addMenu("Edit")
        self.view_menu = menu_bar.addMenu("View")
        self.extra_menu = menu_bar.addMenu("This is intentionally very long to see what happens")

        # Options in file bar
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        self.file.addAction(exitAction)
