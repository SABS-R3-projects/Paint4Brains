"""Paint4Brains Data Manipulation

This script contains the main functions required for manipulating the data required by the software.
Data manipulation includes loading the data, performing any required pre-processing, selecting data and label slices, and manipulating information.
This file consists of several functions. Please check individual documentations for particular infomration.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.BrainData import BrainData

"""

import numpy as np
import nibabel as nib
from Paint4Brains.Extractor import Extractor
from Paint4Brains.Segmenter import Segmenter


class BrainData:
    """BrainData class for Paint4Brains.

    This class contains the main functions required for manipulating the data required by the software.

    Args:
        filename (str): Path leading to the location of the brain data file.
        label_filename (str): Path to the location of the labeled data file.

    """

    def __init__(self, filename, label_filename=None):

        self.filename = filename
        self.label_filename = label_filename
        self.saving_filename = None

        self.__nib_data = nib.load(filename)
        self.__nib_label_data = None
        self.__orientation = nib.orientations.io_orientation(
            self.__nib_data.affine)
        self.nii_img = self.__nib_data
        self.data = np.flip(self.__nib_data.as_reoriented(
            self.__orientation).get_fdata().transpose())

        self.data_unchanged = self.data.copy()

        # Default empty values
        self.different_labels = np.zeros(1, dtype=int)
        self.__current_label = 1
        self.other_labels_data = np.zeros(self.data.shape)
        self.multiple_labels = False

        if self.label_filename is None:
            self.label_data = np.zeros(self.data.shape)
        else:
            self.label_filename = label_filename
            self.load_label_data(label_filename)

        self.section = 0
        self.shape = self.data.shape
        self.i = int(self.shape[self.section] / 2)
        maxim = np.max(self.data)
        self.data = self.data / maxim

        self.intensity = 1.0
        self.scale = 1.0
        self.extracted = False
        self.extraction_cutoff = 0.5
        self.probability_mask = np.zeros(self.shape)
        self.full_head = self.data.copy()
        self.only_brain = []
        self.segmenter = Segmenter()

        self.edit_history = [
            [self.label_data.copy(), self.other_labels_data.copy()]]
        self.edits_recorded = 10
        self.current_edit = 1

    def get_data_slice(self, i):
        """Function returning the 2D MRI slice for a given point

        This function Returns the 2-D slice at point i of the full MRI data (not labels).
        Depending on the desired view (self.section) it returns a different 2-D slice of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation.

        Args:
            i (int): Index point, indicating the desired location where the 2D slice is to be sampled.

        Returns:
            list: 2D slice at point i of the full MRI data
        """
        if self.section == 0:
            return self.data[i]
        elif self.section == 1:
            return np.flip(self.data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.data[:, :, i].transpose(), axis=1)

    @property
    def current_data_slice(self):
        """Returns the current data slice of the brain

        Function returning the 2D slice of the brain input, using the get_data_slice function.

        Returns:
            list: 2-D image representing the view of the brain at the self.i slice from the self.section axis
        """
        return self.get_data_slice(self.i)

    def get_label_data_slice(self, i):
        """Returns the 2-D slice at point i of the labelled data.

        Depending on the desired view (self.section) it returns 2-D slice with respect to a different axis of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation.

        Args:
            i (int): Index point, indicating the desired location where the 2D slice is to be sampled.

        Returns:
            list: 2-D slice at point i of the labelled data
        """
        self.label_data = np.clip(self.label_data, 0, 1)
        if self.section == 0:
            return self.label_data[i]
        elif self.section == 1:
            return np.flip(self.label_data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.label_data[:, :, i].transpose(), axis=1)

    @property
    def current_label_data_slice(self):
        """Returns the current data slice of the label being currently edited

        Function calling the get_label_data_slice to return the current data slice of the label currently being edited.

        Returns:
            list: 2-D image representing the view of the label being currently edited at the self.i slice from the self.section axis
        """
        return self.get_label_data_slice(self.i)

    def get_other_labels_data_slice(self, i):
        """Returns the 2-D slice at point i of all labelled data.

        Depending on the desired view (self.section) it returns 2-D slice with respect to a different axis of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation

        Args:
            i (int): Index point, indicating the desired location where the 2D slice is to be sampled.

        Returns:
            list: 2-D slice at point i of all labelled data
        """
        if self.section == 0:
            return self.other_labels_data[i]
        elif self.section == 1:
            return np.flip(self.other_labels_data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.other_labels_data[:, :, i].transpose(), axis=1)

    @property
    def current_other_labels_data_slice(self):
        """Returns the current data slice of all labels

        Returns:
            list: 2-D image representing the view of all labels at the self.i slice from the self.section axis
        """
        return self.get_other_labels_data_slice(self.i)

    def load_label_data(self, filename):
        """Segmentation labels loader

        Loads a .nii file representing the segmentation labels into the BrainData class.
        It can deal with binary labels or multiple labels. If there were any previous labels loaded, it deletes them.
        It assumes the niifti file for the labels is oriented in the same as the niifti file for the original brain.
        However, it does not assume that the header stored in the file has been updated.

        Args:
            filename (str): Path of the file to load into the GUI
        """
        self.label_filename = filename
        self.__nib_label_data = nib.load(self.label_filename)
        x = np.flip(self.__nib_label_data.as_reoriented(
            self.__orientation).get_fdata().transpose()).astype(np.int8)
        self.different_labels = np.unique(x)
        number_of_labels = len(self.different_labels)
        if number_of_labels == 2:
            self.multiple_labels = False
            self.label_data = x
            self.other_labels_data = np.zeros(x.shape)
            self.__current_label = 1
        elif number_of_labels > 2:
            self.multiple_labels = True
            self.label_data = np.where(x == self.__current_label, 1, 0)
            self.other_labels_data = np.where(self.label_data == 1, 0, x)

    def save_label_data(self, saving_filename):
        """Label Data Saver

        Saves the labeled data currently being edited into a niifti file.
        It currently does not save the header.
        TODO: If required, add the header saver capability.

        Args:
            saving_filename (str): Name of the file to be saved as
        """
        # Updating other_labels_data to include current label
        to_be_saved = np.where(self.label_data == 0, self.other_labels_data, self.current_label)

        image = nib.Nifti1Image(
            np.flip(to_be_saved, axis=(0, 1)).transpose(), self.__nib_data.affine)
        print("Saving labeled data to: " + saving_filename)
        nib.save(image, saving_filename)
        self.saving_filename = saving_filename

    def position_as_voxel(self, mouse_x, mouse_y):
        """3D Mouse Position

        Returns the 3-D position of the mouse with respect to the brain

        Args:
            mouse_x (int): Position of the mouse in the x axis
            mouse_y (int): Position of the mouse in the y axis

        Returns:
            tuple: 3-D position of the mouse (in voxels)
        """
        if self.section == 0:
            return self.i, mouse_x, mouse_y
        elif self.section == 1:
            return self.shape[0] - mouse_y - 1, self.i, self.shape[2] - mouse_x - 1
        elif self.section == 2:
            return self.shape[0] - mouse_y - 1, mouse_x, self.i

    def voxel_as_position(self, i, j, k):
        """2D Mouse Position

        Returns the 2-D position of the mouse from the 3-D position of the Brain

        Args:
            i (int): Brain voxel position on x-axis
            j (int): Brain voxel position on y-axis
            k (int) :Brain voxel position on z-axis

        Returns:
            tuple: 2-D position of the mouse
        """
        if self.section == 0:
            return j, k
        elif self.section == 1:
            return self.shape[2] - k - 1, self.shape[0] - i - 1
        elif self.section == 2:
            return j, self.shape[0] - i - 1

    # Creating class methods #

    def log_normalization(self):
        """Logarithmic Normalization

        A Method that performs a logarithmic normalization on the brain
        """
        if self.extracted:
            self.data = self.only_brain
        else:
            self.data = self.full_head
        self.scale = (np.max(self.data) - np.min(self.data))
        new_brain_data = np.clip(np.log2(1 + self.data.astype(float)) * self.intensity, 0, self.scale)
        self.data = new_brain_data

    def brainExtraction(self):
        """Brain Extraction

        Function which performs brain extraction/skull stripping on nifti images in preparation for segmentation.
        """
        # If it has already been extracted (mostly empty) don't do it again
        if self.extracted:
            return 0
        elif len(self.only_brain) == 0:
            ext = Extractor()
            self.probability_mask = ext.run(self.data)
            mask2 = np.where(self.probability_mask >
                             self.extraction_cutoff, 1, 0)
            self.only_brain = self.data * mask2

        self.data = self.only_brain
        self.extracted = True
        self.nii_img = nib.Nifti1Image(self.data, self.nii_img.affine)

    def full_brain(self):
        """Brain & Head Images

        This function returns the image to the original brain with the head image
        It also returns the background image to the unextracted brain.
        """
        if self.extracted:
            self.data = self.full_head
            self.extracted = False
            self.nii_img = nib.Nifti1Image(self.data, self.nii_img.affine)
            # self.nii_img.set_header = self.__nib_data.header

    def reorient(self, target_axcoords=('L', 'A', 'S')):
        """Image Reorientation

        Function to perform reorientation of image axis in the coronol, saggital and axial planes.

        Args:
            target_axcoords (list): List of target output axis orientations, represented as strings corresponding to the axial (A), saggital (S) and coronal (L) planes.
        """
        orientation = nib.orientations.axcodes2ornt(
            nib.orientations.aff2axcodes(self.nii_img.affine))
        target_orientation = nib.orientations.axcodes2ornt(target_axcoords)
        transformation = nib.orientations.ornt_transform(
            orientation, target_orientation)
        new_tran = nib.orientations.apply_orientation(
            self.nii_img.get_data(), transformation)
        reoriented_img = nib.Nifti1Image(new_tran, self.nii_img.affine)

        self.nii_img = reoriented_img
        data_array = reoriented_img.get_fdata()
        self.data = data_array / np.max(data_array)

    def segment(self, device):
        """Brain Segmenter

        This function calls the Segmenter file to perform brain segmentation.

        Args:
            device (str/int): Device to run the neural network on, can be "cpu" (str) or cuda-enabled GPU, either integrated (int - 0) or external (int - 1)
        """
        try:
            self.segmenter.device = device
            self.segmenter.run = True
            self.label_filename = self.segmenter.segment(self.filename)
        except Exception as e:
            raise e
        else:
            self.load_label_data(self.label_filename)
            self.store_edit()

    @property
    def current_label(self):
        """Current Label Values

        Returns the value of the label currently being edited

        Returns:
            int: Value of label currently being edited
        """
        return self.__current_label

    @current_label.setter
    def current_label(self, new_label):
        """Current Label Setter. 

        Sets the label to be edited.
        It updates both the current label data and the other labels data.
        If the value of the label is not saved, a new label is created using this label as its index.

        Args:
            new_label (int): Next label to be edited
        """
        if new_label not in self.different_labels:
            self.multiple_labels = True
            self.different_labels = np.append(self.different_labels, new_label)
        self.label_data = np.clip(self.label_data, 0, 1)
        other_minus_current = np.where(
            self.other_labels_data == self.__current_label, 0, self.other_labels_data)
        self.other_labels_data = np.where(
            self.label_data == 0, other_minus_current, self.__current_label)
        self.label_data = np.where(self.other_labels_data == new_label, 1, 0)
        self.__current_label = new_label

    def store_edit(self):
        """Function that stores previous edits.

        This list of edits are then used by the undo and redo functions.
        """

        if self.edits_recorded < len(self.edit_history):
            self.edit_history = self.edit_history[1:]
        if self.current_edit < len(self.edit_history):
            self.edit_history = self.edit_history[
                                :(self.current_edit - len(self.edit_history))]

        self.edit_history.append(
            [self.label_data.copy(), self.other_labels_data.copy()])
        self.current_edit = len(self.edit_history)
