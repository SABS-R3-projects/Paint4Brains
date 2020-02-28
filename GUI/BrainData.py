import numpy as np
import nibabel as nib
from deepbrain import Extractor
from Segmenter import segment_default


class BrainData:
    def __init__(self, filename, label_filename=None):
        """ Initialize class

        :str filename: The name and location of the file
        """
        self.filename = filename
        self.label_filename = label_filename
        self.saving_filename = None

        self.__nib_data = nib.load(filename)
        self.__nib_label_data = None
        self.__orientation = nib.orientations.io_orientation(self.__nib_data.affine)
        self.nii_img = self.__nib_data
        self.data = np.flip(self.__nib_data.as_reoriented(self.__orientation).get_fdata().transpose())

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

        self.edit_history = [[self.label_data.copy(), self.other_labels_data.copy()]]
        self.edits_recorded = 20
        self.current_edit = 1

    def get_data_slice(self, i):
        """ Returns the 2-D slice at point i of the full MRI data (not labels).

        Depending on the desired view (self.section) it returns a different 2-D slice of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation.
        """
        if self.section == 0:
            return self.data[i]
        elif self.section == 1:
            return np.flip(self.data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.data[:, :, i].transpose(), axis=1)

    @property
    def current_data_slice(self):
        """ Returns the current data slice of the brain

        :return: 2-D image representing the view of the brain at the self.i slice from the self.section axis
        """
        return self.get_data_slice(self.i)

    def get_label_data_slice(self, i):
        """ Returns the 2-D slice at point i of the labelled data.

        Depending on the desired view (self.section) it returns 2-D slice with respect to a different axis of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation.
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
        """ Returns the current data slice of the label being currently edited

        :return: 2-D image representing the view of the label being currently edited at the self.i slice
        from the self.section axis
        """
        return self.get_label_data_slice(self.i)

    def get_other_labels_data_slice(self, i):
        """ Returns the 2-D slice at point i of all labelled data.

        Depending on the desired view (self.section) it returns 2-D slice with respect to a different axis of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation
        """
        if self.section == 0:
            return self.other_labels_data[i]
        elif self.section == 1:
            return np.flip(self.other_labels_data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.other_labels_data[:, :, i].transpose(), axis=1)

    @property
    def current_other_labels_data_slice(self):
        """ Returns the current data slice of all labels

        :return: 2-D image representing the view of all labels at the self.i slice from the self.section axis
        """
        return self.get_other_labels_data_slice(self.i)

    def load_label_data(self, filename):
        """ Loads a .nii file representing the segmentation labels into the BrainData class.

        It can deal with binary labels or multiple labels. If there were any previous labels loaded, it deletes them.
        It assumes the niifti file for the labels is oriented in the same as the niifti file for the original brain.
        However, it does not assume that the header stored in the file has been updated.
        :param filename: Path of the file to load into the GUI
        """
        self.label_filename = filename
        self.__nib_label_data = nib.load(self.label_filename)
        x = np.flip(self.__nib_label_data.as_reoriented(self.__orientation).get_fdata().transpose()).astype(np.int8)
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
        """ Saves the labeled data currently being edited into a niifti file.

        It currently does not save the header.
        :param saving_filename: Name of the file to be saved as
        """
        self.saving_filename = saving_filename
        print(saving_filename)
        if (saving_filename[0])[-4:] != ".nii":
            saving_filename = saving_filename[0] + ".nii"
        else:
            saving_filename = saving_filename[0]

        image = nib.Nifti1Image(np.flip(self.label_data, axis=(0, 1)).transpose(), self.__nib_data.affine)
        print("Saving labeled data to: " + saving_filename)
        nib.save(image, saving_filename)

    def position_as_voxel(self, mouse_x, mouse_y):
        """ Returns the 3-D position of the mouse with respect to the brain

        :param mouse_x: Position of the mouse in the x axis
        :param mouse_y: Position of the mouse in the y axis
        :return: 3-D position of the mouse (in voxels)
        """
        if self.section == 0:
            return self.i, mouse_x, mouse_y
        elif self.section == 1:
            return self.shape[0] - mouse_y - 1, self.i, self.shape[2] - mouse_x - 1
        elif self.section == 2:
            return self.shape[0] - mouse_y - 1, mouse_x, self.i

    def voxel_as_position(self, i, j, k):
        """ Returns the 2_D position of the mouse from the 3_D position of the Brain
        """
        if self.section == 0:
            return j, k
        elif self.section == 1:
            return self.shape[2] - k - 1, self.shape[0] - i - 1
        elif self.section == 2:
            return j, self.shape[0] - i - 1

    # Creating class methods #

    def log_normalization(self):
        """
        A Method that performs a logarithmic normalization on the brain
        """
        if self.extracted:
            self.data = self.only_brain
        else:
            self.data = self.full_head
        self.scale = (np.max(self.data) - np.min(self.data))
        new_brain_data = np.clip(np.log2(1 + self.data.astype(float) / self.scale) * self.scale * self.intensity, 0, self.scale)
        self.data = new_brain_data

    def brainExtraction(self):
        """Performs brain extraction/skull stripping on nifti images. Preparation for segmentation.

        Arguments:
            self object with self.data {[np.array]} -- .nii image.
        """
        # If it has already been extracted (mostly empty) don't do it again
        if self.extracted:
            return 0
        elif len(self.only_brain) == 0:
            ext = Extractor()
            self.probability_mask = ext.run(self.data)
            print("EXTRACTION DONE")
            mask2 = np.where(self.probability_mask > self.extraction_cutoff, 1, 0)
            self.only_brain = self.data * mask2

        self.data = self.only_brain
        self.extracted = True
        self.nii_img = nib.Nifti1Image(self.data, self.nii_img.affine)

    def full_brain(self):
        """ Returns the image to the original brain + head image

        Returns the background image to the unextracted brain.
        """
        if self.extracted:
            self.data = self.full_head
            self.extracted = False
            self.nii_img = nib.Nifti1Image(self.data, self.nii_img.affine)
            # self.nii_img.set_header = self.__nib_data.header

    def reorient(self, target_axcoords=('L', 'A', 'S')):
        """ Function to perform reorientation of image axis in the coronoal, saggital and axial planes.

        Arguments:
        target_axcoords = list, string -- list of target output axis orientations
        """
        orientation = nib.orientations.axcodes2ornt(nib.orientations.aff2axcodes(self.nii_img.affine))
        target_orientation = nib.orientations.axcodes2ornt(target_axcoords)
        transformation = nib.orientations.ornt_transform(orientation, target_orientation)
        new_tran = nib.orientations.apply_orientation(self.nii_img.get_data(), transformation)
        reoriented_img = nib.Nifti1Image(new_tran, self.nii_img.affine)

        self.nii_img = reoriented_img
        data_array = reoriented_img.get_fdata()
        self.data = data_array / np.max(data_array)

    def segment(self, device):
        """ Segments the brain.

        The logic behind this function is writen in the Segmenter file
        :param device: Device to run the neural network on, can be "cpu or "cuda"
        """
        self.label_filename = segment_default(self.filename, device)
        self.load_label_data(self.label_filename)
        self.store_edit()

    @property
    def current_label(self):
        """ Returns the value of the label currently being edited

        :return: Label currently being edited
        """
        return self.__current_label

    @current_label.setter
    def current_label(self, new_label):
        """ Sets the label to be edited. However, it does a lot more:

        It updates both the current label data and the other labels data.
        If the value of the label is not saved, a new label is created using this label as its index.
        :int new_label: Next label to be edited
        """
        if new_label not in self.different_labels:
            self.multiple_labels = True
            self.different_labels = np.append(self.different_labels, new_label)
        self.label_data = np.clip(self.label_data, 0, 1)
        other_minus_current = np.where(self.other_labels_data == self.__current_label, 0, self.other_labels_data)
        self.other_labels_data = np.where(self.label_data == 0, other_minus_current, self.__current_label)
        self.label_data = np.where(self.other_labels_data == new_label, 1, 0)
        self.__current_label = new_label

    def store_edit(self):
        """ Function that stores previous edits.

        This list of edits are then used by the undo and redo functions.
        """

        if self.edits_recorded < len(self.edit_history):
            self.edit_history = self.edit_history[1:]
        if self.current_edit < len(self.edit_history):
            self.edit_history = self.edit_history[
                                :(self.current_edit - len(self.edit_history))]

        self.edit_history.append([self.label_data.copy(), self.other_labels_data.copy()])
        self.current_edit = len(self.edit_history)
