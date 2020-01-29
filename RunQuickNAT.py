import subprocess
import os
from SettingsGenerator import parser_configurator, get_current_directory

def brainSegmentation():
    """
    Using the outputs from brainExtraction and transformation, this function calls QuickNAT to perform brain segmentation
    This function is re-implementation of the original QuickNAT evaluation pipeline. Details can be found here: https://github.com/ai-med/quickNAT_pytorch

    Arguments:
        self object with .nii image field

    """

    # First, we wish to standardize the MRI scans. This is done using the previous "transformation" function.

    # WE NEED TO RUN THE TRANSFORMATION FIRST< BUT WE WILL WORRY ABOUT THIS AFTER WE GET QUICKNAT TO WORK!!!!!!!!!!!!

    # self.transformation()


    # First, we configurate the .ini settings file
    parser_configurator()

    current_director = get_current_directory()

    quickNAT_director = current_director+'/quickNAT_pythorch/'

    os.chdir(quickNAT_director)

    subprocess.run(["python","run.py","--mode=eval_bulk"])

    os.chdir(current_director)

if __name__ == '__main__':
    brainSegmentation()
