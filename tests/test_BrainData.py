import os
import unittest
import numpy as np

from Paint4Brains.BrainData import BrainData


class TestBrainData(unittest.TestCase):
    """Test class methods in BrainData
    """
    rootdir = os.path.split(os.getcwd())[0]
    filename = os.path.join(rootdir, 'Paint4Brains/opensource_brains/H_F_22.nii')
    brain = BrainData(filename)


    def test_load_BrainData(self):
        #test filename points to the correct directory
        assert  self.filename == self.brain.filename

    def test_current_data_slice(self):
        #test current_brain_slice returns the correct shape
        assert  len(self.brain.current_data_slice.shape) == 2
        assert  self.brain.current_data_slice.shape == self.brain.get_data_slice(self.brain.i).shape

    def test_get_data_slice(self):
        #test get_data_slice returns a 2d array from the 3d data object
        dimensions = len(self.brain.data.shape)
        for j in range(dimensions):
            self.brain.section = j
            assert  len(self.brain.get_data_slice(self.brain.i).shape) == 2

    def test_current_data_slice_label(self):
        #test current_brain_slice returns the correct shape
        assert  len(self.brain.current_label_data_slice.shape) == 2
        assert  self.brain.current_label_data_slice.shape == self.brain.get_label_data_slice(self.brain.i).shape

    def test_get_data_slice_label(self):
        #test get_data_slice returns a 2d array from the 3d data object
        dimensions = len(self.brain.data.shape)
        for j in range(dimensions):
            self.brain.section = j
            assert  len(self.brain.get_label_data_slice(self.brain.i).shape) == 2
            #test data and labels have the same dimensions
            assert  len(self.brain.get_data_slice(self.brain.i).shape) == len(self.brain.get_label_data_slice(self.brain.i).shape)
            #test data and labels are the same size
            assert self.brain.get_label_data_slice(self.brain.i).shape == self.brain.get_data_slice(self.brain.i).shape

    def test_log_normalistion(self):
        #skull stripping has not been performed so brain.data should equal brain.full_head
        #assert  self.brain.data == self.brain.full_head

        #test log scaling factor is not greater than max value in brain.data
        assert  self.brain.scale <= np.max(self.brain.data)

        #test variance of data array. Expect higher variance after log normalising (more contrast).
        test_brain = BrainData(self.filename)
        test_brain.log_normalization()

        assert  np.var(self.brain.data) <= np.var(test_brain.data)

        del test_brain

    def test_brain_Extraction(self):
        test_brain = BrainData(self.filename)
        test_brain.brainExtraction()

        #check data and probability mask are the same shape
        assert  self.brain.data.shape == test_brain.probability_mask.shape

        #test number of zero values increases afte brain exrtraction
        assert  np.count_nonzero(self.brain.data==0) <= np.count_nonzero(test_brain.data==0)
        


class TestDummyTest(unittest.TestCase):
    a = 2

    def test_value_of_a(self):
        assert  self.a == 2
