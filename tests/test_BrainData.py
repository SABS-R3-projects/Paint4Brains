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

        assert  self.filename == self.brain.filename

    def test_current_data_slice(self):
        assert  self.brain.current_data_slice.shape == self.brain.get_data_slice(self.brain.i).shape

    def test_get_data_slice(self):

        dimensions = len(self.brain.data.shape)
        for i in range(dimensions):
            brain.section = i
            random_slices = np.random.randint(low=0, high=min(self.brain.data.shape), size = 10)
            for j in random_slices:
                assert  len(self.brain.get_data_slice(j).shape) == 2




class TestDummyTest(unittest.TestCase):
    a = 2

    def test_value_of_a(self):
        assert  self.a == 2
