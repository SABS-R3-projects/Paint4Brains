import os
import unittest

from Paint4Brains.BrainData import BrainData


class TestBrainData(unittest.TestCase):
    """Test class methods in BrainData
    """
    rootdir = os.path.split(os.getcwd())[0]
    filename = os.path.join(rootdir, 'Paint4Brains/opensource_brains/H_F_22.nii')
    brain = BrainData(filename)

    def test_load_BrainData(self):
        assert  self.filename == self.brain.filename

    

class TestDummyTest(unittest.TestCase):
    a = 2

    def test_value_of_a(self):
        assert  self.a == 2
