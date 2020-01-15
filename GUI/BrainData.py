import numpy as np
import nibabel as nib


class BrainData:
    def __init__(self, filename, label_filename = None):
        """ Initialize class

        :str filename: The name and location of the file
        """
        self.filename = filename
        self.label_filename = label_filename
        self.saving_filename = None

        self.__nib_data = nib.load(filename)
        self.__nib_label_data = None
        self.__orientation = nib.orientations.io_orientation(self.__nib_data.affine)
        self.data = np.flip(self.__nib_data.as_reoriented(self.__orientation).get_fdata().transpose())

        if self.label_filename is None:
            self.label_data = np.zeros(self.data.shape)
        else:
            self.label_filename = label_filename
            self.load_label_data(label_filename)

        self.section = 0
        self.shape = self.data.shape
        self.i = int(self.shape[self.section] / 2)
        maxim = np.max(self.data)
        self.data = self.data/maxim

        self.different_labels = [0]
        self.current_label = 1
        self.other_labels_data = np.zeros(self.shape)

    def get_data_slice(self, i):
        """ Returns the 2-D slice at point i of the full MRI data (not labels).

        Depending on the desired view (self.section) it returns a different 2-D slice of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation
        """
        if self.section == 0:
            return self.data[i]
        elif self.section == 1:
            return np.flip(self.data[:, i].transpose())
        elif self.section == 2:
            return np.flip(self.data[:, :, i].transpose(), axis=1)

    @property
    def current_data_slice(self):
        return self.get_data_slice(self.i)

    def get_label_data_slice(self, i):
        """ Returns the 2-D slice at point i of the labelled data.

        Depending on the desired view (self.section) it returns 2-D slice with respect to a different axis of the 3-D data.
        A number of transposes and flips are done to return the 2_D image with a sensible orientation
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
        return self.get_label_data_slice(self.i)

    def get_other_labels_data_slice(self, i):
        """ Returns the 2-D slice at point i of the other labelled data.

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
        return self.get_other_labels_data_slice(self.i)

    def load_label_data(self, filename):
        """ Loads a given 3-D binary array (x) into the GUI.
        """
        self.label_filename = filename
        self.__nib_label_data = nib.load(self.label_filename)
        x = np.flip(self.__nib_label_data.as_reoriented(self.__orientation).get_data().transpose()).astype(np.int8)
        self.other_labels_data = x
        self.different_labels = np.unique(x)
        number_of_labels = len(self.different_labels)
        if number_of_labels == 2:
            self.label_data = x
        elif number_of_labels > 2:
            self.label_data = np.where(x == self.different_labels[1], 1, 0)

    def save_label_data(self, saving_filename):

        self.saving_filename = saving_filename
        if saving_filename[1] != "Nii Files (*.nii)":
            return
        elif (saving_filename[0])[-4:] != ".nii":
            saving_filename = saving_filename[0] + ".nii"
        else:
            saving_filename = saving_filename[0]

        image = nib.Nifti1Image(np.flip(self.label_data).transpose(), np.eye(4))
        print("Saving labeled data to: " + saving_filename)
        nib.save(image, saving_filename)

    def position_as_voxel(self, mouse_x, mouse_y):
        if self.section == 0:
            return self.i, mouse_x, mouse_y
        elif self.section == 1:
            return self.shape[0] - mouse_y - 1, self.i, self.shape[2] - mouse_x - 1
        elif self.section == 2:
            return self.shape[0] - mouse_y - 1, mouse_x, self.i

