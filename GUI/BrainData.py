import numpy as np
import nibabel as nib
from deepbrain import Extractor
import nilearn as nl
import os
import pathlib
import configparser
import subprocess

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

        # Default empty values
        self.different_labels = np.zeros(1, dtype= int)
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
        self.data = self.data/maxim

        self.extracted = False
        self.extraction_cutoff = 0.5
        self.full_head = self.data.copy()
        self.only_brain = []

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
        x = np.flip(self.__nib_label_data.as_reoriented(self.__orientation).get_data().transpose()).astype(np.int8)
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

    ### Creating class methods ###
    def brainExtraction(self):
        """Performs brain extraction/skull stripping on nifti images. Preparation for segmentation.

        Arguments:
            self object with self.data {[np.array]} -- .nii image
        """
        # If it has already been extracted (mostly empty) don't do it again
        if self.data.size > 2*np.count_nonzero(self.data):
            print("INPUT BRAIN IS ALREADY EXTRACTED")
            return 0
        if self.extracted:
            return 0
        elif len(self.only_brain) == 0:
            ext = Extractor()
            prob = ext.run(self.data)
            print("EXTRACTION DONE")
            mask2 = np.where(prob > self.extraction_cutoff, 1, 0)
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
            #self.nii_img.set_header = self.__nib_data.header

    def reorient(self, target_axcoords = ('L','A','S')):
        """ Function to perform reorientation of image axis in the coronoal, saggital and axial planes.

        Arguments:
        target_axcoords = list, string -- list of target output axis orientations
        """
        orientation = nib.orientations.axcodes2ornt(nib.orientations.aff2axcodes(self.nii_img.affine))
        target_orientation = nib.orientations.axcodes2ornt(target_axcoords)
        transformation = nib.orientations.ornt_transform(orientation, target_orientation)
        new_tran = nib.orientations.apply_orientation(self.nii_img.get_data(),transformation)
        reoriented_img = nib.Nifti1Image(new_tran, self.nii_img.affine)

        self.nii_img = reoriented_img
        data_array = reoriented_img.get_fdata()
        self.data = data_array / np.max(data_array)

    def transformation(self):
        '''Transform Nifti images to FreeSurfer standard with 1x1x1 voxel dimension
        Arguments:
        self object with .nii image field
        zooms: int -- voxel dimensions
        shape: int -- image resampling dimensions
        target_axcoords: list, string -- list of target output axis orientations
        '''

        zooms = (1, 1, 1) 
        shape = (256, 256, 256)
        target_axcoords = ('L','I','A')

        self.zooms = zooms
        self.shape = shape

        # setting affine for size and dimension
        target_affine = nib.volumeutils.shape_zoom_affine(shape, zooms, x_flip=True)

        # creating new image with the new affine and shape
        new_img = nl.image.resample_img(self.nii_img, target_affine, target_shape=shape)

        # change orientation
        orientation = nib.orientations.axcodes2ornt(nib.orientations.aff2axcodes(new_img.affine))
        target_orientation = nib.orientations.axcodes2ornt(target_axcoords)
        transformation = nib.orientations.ornt_transform(orientation, target_orientation)

        # apply transformation with new affine and orientation
        data = new_img.get_fdata()
        new_tran = nib.orientations.apply_orientation(data, transformation)
        transformed_image = nib.Nifti1Image(new_tran, target_affine)
        transformed_data = new_tran

        # update self variables
        self.affine = transformed_image.affine
        self.nii_img = transformed_image
        # self.data = transformed_data

        #### ANDREI's bit #####

        # Get the current directory, and then change to the optput path
        current_directory = os.path.dirname(os.path.realpath(__file__))
        dir_path2 = current_directory.rstrip("/GUI") + "/quickNAT_pythorch/data_input/"

        # Save the transformed filetype as input to QuickNAT
        filename = 'transformed.nii'
        nib.save(self.nii_img, dir_path2 + filename)

        # Change the directory to modify the test_list input to QuickNAT
        os.chdir(dir_path2.rstrip("data_input/"))

        # Clear the content of test_list, and then write the new filename
        open('test_list.txt','w').close()
        test_list = open('test_list.txt','w')
        test_list.writelines(filename)
        test_list.close()

        # Change the directory back to the original working one
        os.chdir(current_directory)

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
        self.other_labels_data = np.where(self.label_data == 0,  self.other_labels_data, self.__current_label)
        self.label_data = np.where(self.other_labels_data == new_label, 1, 0)
        self.__current_label = new_label


    def brainSegmentation(self):
        """
        Using the outputs from brainExtraction and transformation, this function calls QuickNAT to perform brain segmentation
        This function is re-implementation of the original QuickNAT evaluation pipeline. Details can be found here: https://github.com/ai-med/quickNAT_pytorch

        Arguments:
            self object with .nii image field

        """

        # First, we wish to standardize the MRI scans. This is done using the previous "transformation" function.

        self.transformation()

        original_directory = os.path.dirname(os.path.realpath(__file__))
        quickNAT_director = original_directory.rstrip("/GUI") + "/quickNAT_pythorch/"

        def read_original_configurator(file_path):

            """
            This  nested function reads the original configuration file and returns all the values contained within in.
           
            Returns:
                setting_dictionary (dict): dictionary containing the original configuration file information

            """

            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(file_path+'/settings_eval_original.ini')
            sections = config.sections()
            settings_dictionary = {}
            options = config.options(sections[0])
            for option in options:
                try:
                    settings_dictionary[option] = config[sections[0]][option]
                    if settings_dictionary[option] == -1:
                        DebugPring("skip: %s" % option)
                except:
                    print("Exception on %s!" % option)
                    settings_dictionary[option] = None

            return sections[0], settings_dictionary

        def parser_configurator(file_path):
            """
            This nested function prints out the current settings, asks for a user input to update the settings and creates a new settings file.
            This function will need to be changed once the GUI settings window is created! 

            """

            section_name, settings_dictionary = read_original_configurator(file_path)

            config = configparser.ConfigParser()

            inputs = []

            for key in settings_dictionary:
                if key == 'device':
                    print("Provide CPU or ID of GPU (0 or 1) you want to excecute your code, or press Enter to leave default")
                    data_input = input("Your input:")
                    if data_input == "":
                        single_input = settings_dictionary[key]
                    else:
                        single_input = data_input
                elif key == 'coronal_model_path':
                    single_input = settings_dictionary[key]
                elif key == 'axial_model_path':
                    single_input = settings_dictionary[key]
                elif key == 'data_dir':
                    single_input = '"'+file_path+'data_input'+'"'
                elif key == 'directory_struct':
                    print("Valid options for data directory structure are >> FS <<  or >> Linear <<. If you input data directory is similar to FreeSurfer, i.e. data_dir/<Data_id>/mri/orig.mgz then use >> FS <<. If the entries are data_dir/<Data_id> use >> Linear <<. To leave at default, press Enter")
                    data_input = input("Provide information about input directory structure: ")
                    if data_input == "":
                        single_input = settings_dictionary[key]
                    else:
                        single_input = data_input
                elif key == 'volumes_txt_file':
                    single_input = settings_dictionary[key]
                elif key == 'batch_size':
                    single_input = settings_dictionary[key]
                elif key == 'save_predictions_dir':
                    single_input = '"'+file_path+'output_file'+'"'
                elif key == 'view_agg':
                    single_input = settings_dictionary[key]
                elif key == 'estimate_uncertainty':
                    single_input = settings_dictionary[key]
                elif key == 'mc_samples':
                    single_input = settings_dictionary[key]

                inputs.append(str(single_input))
            
            output_directory = file_path
            
            cfgfile = open(output_directory+"settings_eval.ini",'w')
            config.add_section(section_name)

            for idx, key in enumerate(settings_dictionary):
                config.set(section_name, key ,inputs[idx])

            config.write(cfgfile)
            cfgfile.close()

        parser_configurator(quickNAT_director)

        os.chdir(quickNAT_director)

        subprocess.run(["python","run.py","--mode=eval_bulk"])

        os.chdir(original_directory)