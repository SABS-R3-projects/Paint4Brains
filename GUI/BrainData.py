import numpy as np
import nibabel as nib


class BrainData:
    def __init__(self, filename):
        """ Initilaize class

        :str filename: The name and location of the file
        """
        self.filename = filename
        self.label_filename = ""
        self.data = np.flip(nib.as_closest_canonical(nib.load(filename)).get_fdata().transpose())
        self.label_data = np.zeros(self.data.shape)
        self.section = 0
        self.shape = self.data.shape

    def get_data(self, i):
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

    def get_label_data(self, i):
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

    def set_label_data(self, i, x):
        """ Sets the data at a certain slice i to the 2-D array x.

        Depending on the desired view (self.section) it sets a 2-D slice with respect to a different axis of the 3-D data
        This function is not currently used.
        """
        if self.section == 0:
            self.label_data[i] = x
        elif self.section == 1:
            self.label_data[:, i] = np.flip(x.transpose())
        elif self.section == 2:
            self.label_data[:, :, i] = np.flip(x.transpose(), axis=1)

    def load_label_data(self, filename):
        """ Loads a given 3-D binary array (x) into the GUI.
        """
        self.label_filename = filename
        x = np.flip(nib.as_closest_canonical(nib.load(self.label_filename)).get_data().transpose())
        self.label_data = x.astype(np.int8)

    def save_label_data(self, saving_filename):

        if saving_filename[1] != "Nii Files (*.nii)":
            return
        elif (saving_filename[0])[-4:] != ".nii":
            saving_filename = saving_filename[0] + ".nii"
        else:
            saving_filename = saving_filename[0]

        image = nib.Nifti1Image(np.flip(self.main_widget.label_data).transpose(), np.eye(4))
        print("Saving labeled data to: " + saving_filename)
        nib.save(image, saving_filename)

    def position_as_voxel(self, i, mouse_x, mouse_y):
        if self.section == 0:
            return i, mouse_x, mouse_y
        elif self.section == 1:
            return self.shape[0] - mouse_y - 1, i, self.shape[2] - mouse_x - 1
        elif self.section == 2:
            return self.shape[0] - mouse_y - 1, mouse_x, i

