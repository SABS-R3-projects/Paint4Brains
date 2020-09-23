import os
import unittest
import numpy as np

from Paint4Brains.BrainData import BrainData


class TestBrainData(unittest.TestCase):
    """Test class methods in BrainData
    """
    rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filename = os.path.join(rootdir, '../Paint4Brains/opensource_brains/H_F_22.nii')
    brain = BrainData(filename)

    def test_load_BrainData(self):
        """testing initialisation of BrainData object
        to be completed
        """
        # test filename points to the correct directory
        assert self.filename == self.brain.filename

    def test_current_data_slice(self):
        """testing current_data_slice function
        """
        # test current_brain_slice returns the correct shape
        assert len(self.brain.current_data_slice.shape) == 2
        assert self.brain.current_data_slice.shape == self.brain.get_data_slice(self.brain.i).shape

    def test_get_data_slice(self):
        """testing get_data_slice function
        """
        # test get_data_slice returns a 2d array from the 3d data object
        dimensions = len(self.brain.data.shape)
        for j in range(dimensions):
            self.brain.section = j
            assert len(self.brain.get_data_slice(self.brain.i).shape) == 2

    def test_current_data_slice_label(self):
        """testing current_label_data_slice function
        """
        # test current_brain_slice returns the correct shape
        assert len(self.brain.current_label_data_slice.shape) == 2
        assert self.brain.current_label_data_slice.shape == self.brain.get_label_data_slice(self.brain.i).shape

    def test_get_data_slice_label(self):
        """testing get_label_data_slice function
        """
        # test get_data_slice returns a 2d array from the 3d data object
        dimensions = len(self.brain.data.shape)
        for j in range(dimensions):
            self.brain.section = j
            assert len(self.brain.get_label_data_slice(self.brain.i).shape) == 2
            # test data and labels have the same dimensions
            assert len(self.brain.get_data_slice(self.brain.i).shape) == len(
                self.brain.get_label_data_slice(self.brain.i).shape)
            # test data and labels are the same size
            assert self.brain.get_label_data_slice(self.brain.i).shape == self.brain.get_data_slice(self.brain.i).shape

    def test_log_normalistion(self):
        """testing log_normalisation function
        """

        # test log scaling factor is not greater than max value in brain.data
        assert self.brain.scale <= np.max(self.brain.data)

        # test variance of data array. Expect higher variance after log normalising (more contrast).
        test_brain = BrainData(self.filename)
        test_brain.log_normalization()

        assert np.var(self.brain.data) <= np.var(test_brain.data)

        # delete test_brain
        del test_brain

    def test_brain_Extraction(self):
        """testing brainExtraction and full_brain functions
        """
        test_brain = BrainData(self.filename)
        test_brain.brainExtraction()

        # check data and probability mask are the same shape
        assert self.brain.data.shape == test_brain.probability_mask.shape

        # test number of zero values increases afte brain exrtraction
        assert np.count_nonzero(self.brain.data == 0) <= np.count_nonzero(test_brain.data == 0)

        # test data shape does not change
        assert self.brain.data.shape == test_brain.data.shape

        # test full_brain to undo extraction
        test_brain.full_brain()
        assert np.count_nonzero(self.brain.data == 0) == np.count_nonzero(test_brain.data == 0)

        # delete test_brain
        del test_brain

    def test_loading_and_saving(self):
        """testing loading and saving labelled data to disk functions.
        """
        # Make a test brain
        test_brain = BrainData(self.filename)

        # Fix the label we are editing
        test_brain.current_label = np.random.randint(2, 12)

        # randomly set labels
        matrix = np.random.randint(0, 12, test_brain.shape)
        test_brain.other_labels_data = matrix

        # save label values to file
        save_file = "test_save.nii"
        test_brain.save_label_data(save_file)

        # check the file was saved
        assert os.path.exists(save_file)

        # clear label values
        test_brain.other_labels_data = np.zeros(test_brain.shape)

        # load label values form file
        test_brain.load_label_data(save_file)

        # compare original labels and loaded ones
        assert np.sum(test_brain.other_labels_data) + test_brain.current_label * np.sum(
            test_brain.label_data) == np.sum(matrix)

        # clear saved files and reset other_labels to zero
        os.remove(save_file)
        test_brain.other_labels_data = np.zeros(test_brain.shape)

    def test_voxel_to_mouse(self):
        """testing transformation from 2D mouse pointer position to 3D voxel location
        """
        # define where the mouse would be
        mouse_x = np.random.randint(0, 20)
        mouse_y = np.random.randint(0, 20)
        self.brain.i = np.random.randint(0, 20)

        # check it works for all views (sections)
        for i in range(3):
            self.brain.section = i

            # transform it into a 3D position
            position = self.brain.position_as_voxel(mouse_x, mouse_y)

            # check position is within the dimensions
            assert 0 <= position[0] < self.brain.shape[0]
            assert 0 <= position[1] < self.brain.shape[1]
            assert 0 <= position[2] < self.brain.shape[2]

            # transform it back into the mouse position and compare
            assert (mouse_x, mouse_y) == self.brain.voxel_as_position(position[0], position[1], position[2])

    def test_current_label_changing(self):
        """testing the changing label properties
        """
        # Setting current label to one (arbitrary but different to second label)
        first_label = np.random.randint(1, 5)
        self.brain.current_label = first_label

        # Setting a random label voxel to one
        x, y, z = np.random.randint(0, 20, 3)
        self.brain.label_data[x, y, z] = 1

        # Changing current label
        second_label = np.random.randint(5, 10)
        self.brain.current_label = second_label

        # Check if the changed value is in other labels
        assert self.brain.other_labels_data[x, y, z] == first_label
        assert self.brain.label_data[x, y, z] == 0

        # Changing it back to the first label
        self.brain.current_label = first_label

        # Check edit is still saved
        assert self.brain.other_labels_data[x, y, z] == first_label
        assert self.brain.label_data[x, y, z] == 1

    def test_edit_history(self):
        """testing store_edits function"""

        # Set edits recorded to a manageable amount
        self.brain.edits_recorded = 1

        # Make an edit
        x, y, z = np.random.randint(0, 10, 3)
        self.brain.label_data[x, y, z] = 1
        self.brain.store_edit()

        # Make another edit
        x2, y2, z2 = np.random.randint(10, 20, 3)
        self.brain.label_data[x2, y2, z2] = 1
        self.brain.store_edit()

        # Check edits worked as expected
        assert self.brain.label_data[x2, y2, z2] == 1
        assert self.brain.label_data[x, y, z] == 1

        # Undo one edit:
        current = self.brain.current_edit
        if current > 1:
            self.brain.label_data = self.brain.edit_history[current - 2][0]
            self.brain.current_edit = self.brain.current_edit - 1

        assert self.brain.label_data[x2, y2, z2] == 0
        assert self.brain.label_data[x, y, z] == 1

        # Undo second edit.
        # This undo shouldn't work because the limit of stored edits is 1:
        current = self.brain.current_edit
        if current > 1:
            self.brain.label_data = self.brain.edit_history[current - 2][0]
            self.brain.current_edit = self.brain.current_edit - 1

        assert self.brain.label_data[x2, y2, z2] == 0
        assert self.brain.label_data[x, y, z] == 1
