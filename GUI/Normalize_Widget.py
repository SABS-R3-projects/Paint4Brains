from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget
#from GUI.MainWindow import MainWindow
#from MainWindow import MainWindow


class NormalizationWidget(QWidget):
    def __init__(self):
        #MainWindow.setObjectName("MainWindow")
       # MainWindow.resize(486, 552)
       # self.centralwidget = QtWidgets.QWidget(MainWindow)
        super(NormalizationWidget, self).__init__()
        self.layout = QtWidgets.QHBoxLayout(self)
        self.tabWidget = QtWidgets.QTabWidget()
        self.setMinimumHeight(120)
        self.setMaximumWidth(400)
        self.tabWidget.setGeometry(QtCore.QRect(170, 30, 211, 111)) #170, 30, 211, 111
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalSlider_2 = QtWidgets.QSlider(self.tab)
        self.horizontalSlider_2.setGeometry(QtCore.QRect(0, 40, 100, 29)) #0, 40, 201, 29
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 20, 171, 17))
        self.label.setObjectName("label")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalSlider_3 = QtWidgets.QSlider(self.tab_2)
        self.horizontalSlider_3.setGeometry(QtCore.QRect(0, 40, 201, 29))
        self.horizontalSlider_3.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_3.setObjectName("horizontalSlider_3")
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setGeometry(QtCore.QRect(10, 20, 171, 17))
        self.label_2.setObjectName("label_2")
        self.horizontalSlider_3.raise_()
        self.horizontalSlider_3.raise_()
        self.label_2.raise_()
        self.tabWidget.addTab(self.tab_2, "")

        #MainWindow.setCentralWidget(self.centralwidget)
        #self.actionNormalize = QtWidgets.QAction(MainWindow)
        #self.actionNormalize.setObjectName("actionNormalize")

        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "Logarithmic Adjustment"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Logarithmic"))
        self.label_2.setText(_translate("MainWindow", "Gaussian Adjustment"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Gaussian"))
        #self.actionNormalize.setText(_translate("MainWindow", "Normalize"))

        #self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        self.layout.addWidget(self.tabWidget)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)
