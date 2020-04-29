"""Optional Sliders Module

This file contains a class requried for creating optional sliders, such as the ones controlling label transparency or extraction tolerance.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.GUI.OptionalSliders import OptionalSliders
        optional_sliders.addWidget(OptionalSliders(parameters))

"""

from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout, QVBoxLayout, QSpacerItem, QLabel
from PyQt5.QtCore import Qt
import numpy as np


class OptionalSliders(QWidget):
    """OptionalSliders class

    A class requried for creating optional sliders, such as the ones controlling label transparency or extraction tolerance.

    Args:
        win (class): ImageViewer class
    """

    def __init__(self, win):
        super(OptionalSliders, self).__init__()
        # Allowing the sliders access to data:
        self.win = win
        self.brain = self.win.brain

        # Building the layout:
        self.layout = QVBoxLayout(self)

        self.label1 = QLabel("Label Transparency")
        self.layout.addWidget(self.label1)

        self.first_slider = QSlider()
        self.first_slider.setOrientation(Qt.Horizontal)
        self.first_slider.setMinimum(0)
        self.first_slider.setMaximum(100)
        self.first_slider.setValue(70)
        self.first_slider.valueChanged.connect(self.transparency_set)
        self.layout.addWidget(self.first_slider)

        self.label2 = QLabel("Extraction Tolerance")
        self.layout.addWidget(self.label2)

        self.second_slider = QSlider()
        self.second_slider.setOrientation(Qt.Horizontal)
        self.second_slider.setMinimum(0)
        self.second_slider.setMaximum(98)
        self.second_slider.setValue(50)
        self.second_slider.valueChanged.connect(self.extraction_probability)
        self.layout.addWidget(self.second_slider)

    def transparency_set(self):
        """Transparency set

        Function which controls the slider setting the transparency of the labels.
        """
        self.win.mid_img.setOpacity(self.first_slider.value()/100)
        self.win.over_img.setOpacity(self.first_slider.value() / 100)
        self.win.refresh_image()

    def extraction_probability(self):
        """Extraction probability

        Function which controls controls the slider setting for defining the extraction tolerance.
        """
        self.brain.extraction_cutoff = (self.second_slider.value()**2-1)/10000
        if len(self.brain.only_brain) == 0:
            self.brain.brainExtraction()
        self.brain.data = np.where(
            self.brain.probability_mask > self.brain.extraction_cutoff, 1, 0)*self.brain.full_head
        self.win.refresh_image()
