"""Slider module

This file contains a collection of functions which implement the slider to be used within the GUI. 

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.Slider import Slider

        window = widget_slider = Slider(parameters)

"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSlider, QSpacerItem, \
    QVBoxLayout, QWidget


class Slider(QWidget):
    """Slider class.

    Implements the slider to be used in the GUI.
    Basically a number of nested Horizontal and Vertical Layouts, with a label showing the current value and a slider imported from Qt. 
    Each time the slider in the gui is moved, the value of self.x and the label are updated by the method set_label_value

    Args:
        minimum (int): Minimum slider value
        maximum (int): Maximum slider value
        parent (class): Base or parent class
    """

    def __init__(self, minimum, maximum, parent=None):
        super(Slider, self).__init__(parent=parent)
        self.horiLayout = QHBoxLayout(self)
        self.label = QLabel(self)
        self.horiLayout.addWidget(self.label)
        self.verticalLayout = QVBoxLayout()
        spacerItem = QSpacerItem(
            20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.slider = QSlider(self)
        self.slider.setMinimum(0)
        self.slider.setOrientation(Qt.Horizontal)
        self.verticalLayout.addWidget(self.slider)
        self.horiLayout.addLayout(self.verticalLayout)
        self.resize(self.sizeHint())

        self.minimum = minimum
        self.maximum = maximum
        self.slider.valueChanged.connect(self.set_label_value)
        self.x = None
        self.set_label_value(self.slider.value())
        # Changing the style is a thing
        # self.setStyleSheet("QSlider::groove:horizontal{height: 10px;margin: 00;}\n"
        #                                 "QSlider::handle:horizontal {background-color: black; border: 1px; height:40px;width: 40px;margin: 00;}\n"
        #                                 "")

    def set_label_value(self, value):
        """Label value

        Function to be called each time slider is moved.
        Updates the label and the stored value.

        Args:
            value (wrapper): Value by which the slider has moved
        """
        self.x = int(self.minimum + (float(value) / (self.slider.maximum() - self.slider.minimum())) * (
            self.maximum - self.minimum))
        self.label.setText("Slice: \n{0:.4g}".format(self.x))
