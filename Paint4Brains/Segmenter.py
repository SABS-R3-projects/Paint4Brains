"""Paint4Brains Segmenter

This file contains the relevant functions for producing the segmented labeled brains, a core function of the Paint4Brains Software.
The functions and methods in this file were extracted from the several files associated with the original QuickNAT implementation.

Attributes:
    label_names (list): List of all labels corresponding to the different regions that QuickNAT is able to segment.
    new_affine (np.array): Homogenous affine giving relationship between voxel coordinates and world coordinates for the segmented files.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.Segmenter import Segmenter
        segmentation_operation = Segmenter(parameters)
        segmentation_operation.segment(file_path)
"""

import os
import nibabel as nib
from nilearn.image import resample_img
import numpy as np
import torch

label_names = ["vol_ID", "Background", "Left WM", "Left Cortex", "Left Lateral ventricle", "Left Inf LatVentricle",
               "Left Cerebellum WM", "Left Cerebellum Cortex", "Left Thalamus", "Left Caudate", "Left Putamen",
               "Left Pallidum", "3rd Ventricle", "4th Ventricle", "Brain Stem", "Left Hippocampus", "Left Amygdala",
               "CSF (Cranial)", "Left Accumbens", "Left Ventral DC", "Right WM", "Right Cortex",
               "Right Lateral Ventricle", "Right Inf LatVentricle", "Right Cerebellum WM",
               "Right Cerebellum Cortex", "Right Thalamus", "Right Caudate", "Right Putamen", "Right Pallidum",
               "Right Hippocampus", "Right Amygdala", "Right Accumbens", "Right Ventral DC"]

new_affine = np.array([[-1, 0., 0, 128],
                       [0., 0., 1, -128],
                       [0., -1, 0, 128],
                       [0., 0., 0, 1]])


class Segmenter:
    """Segmenter class for Paint4Brains.

    This class contains the main segmentation functions required for performing the segmentation operation.

    Args:
        coronal_model_path (str): Path to the pre-trained coronal QuickNAT model
        axial_model_path (str): Path to the pre-trained axial QuickNAT model
        device (int/str): Device type used for training (int - GPU id, str- CPU)

    Returns:
        filename (str): The file name of the outputted segmentation file.

    """

    def __init__(self, device="cpu", coronal_model_path=None, axial_model_path=None):
        # Defining Values to be read by GUI:
        self.state = "Not running"
        self.completion = 0
        self.run = True

        self.cuda_available = torch.cuda.is_available()
        # Take input;
        self.device = device
        # We assume required files are in a fixed directory with respect to this file
        current_directory = os.path.dirname(os.path.realpath(__file__))
        if coronal_model_path is None:
            self.coronal_model_path = current_directory + "/saved_models/finetuned_alldata_coronal.pth.tar"
        else:
            self.coronal_model_path = coronal_model_path
        if axial_model_path is None:
            self.axial_model_path = current_directory + "/saved_models/finetuned_alldata_axial.pth.tar"
        else:
            self.axial_model_path = axial_model_path
        self.original = None

    def _segment_over_one_axis(self, file_path, orientation):

        """Forward Segmentation Pass

        This function segments given volume along one orientation.

        Given the file_path and orientation it returns the probability of each voxel being in one of the 33 possible classes.

        This function loads a volume for segmentation, preprocesses it and then performs a forward pass through the model.

        Args:
            file_path (str): Path to the desired input brain file
            orientation (str): String indicating the input orientation of the file

        Updates:
            self.volume_prediction (np.array): Array containing the predicted labelled data probabilities.
        """

        volume = load_and_preprocess(file_path, orientation=orientation)
        volume = volume if len(
            volume.shape) == 4 else volume[:, np.newaxis, :, :]

        volume = torch.tensor(volume).type(torch.FloatTensor)

        if orientation == "COR":
            self.state = "Segmenting slices along the coronal axis"
            self.volume_prediction = self.volume_prediction.transpose((3, 1, 0, 2))
            model = torch.load(self.coronal_model_path,
                               map_location=torch.device(self.device))
        elif orientation == "AXI":
            self.state = "Segmenting slices along the axial axis"
            self.volume_prediction = self.volume_prediction.transpose((2, 1, 3, 0))
            model = torch.load(self.axial_model_path,
                               map_location=torch.device(self.device))

        model.eval()

        for i in range(len(volume)):
            if not self.run:
                self.state = "Not running"
                self.completion = 0
                # Killed segmentation so clearing memory
                self.volume_prediction = 0
                raise (Exception("Segmentation has been killed"))
            self.completion = self.completion + 50 / 256
            batch_x = volume[i:i + 1]
            if self.cuda_available and self.device == "cuda":
                batch_x = batch_x.cuda(self.device)
            self.volume_prediction[i] += np.squeeze(model(batch_x).cpu().numpy().astype(np.half))

        if orientation == "COR":
            self.volume_prediction = self.volume_prediction.transpose((2, 1, 3, 0))
            self.state = "Finished segmentation along the coronal axis"
        elif orientation == "AXI":
            self.volume_prediction = self.volume_prediction.transpose((3, 1, 0, 2))
            self.state = "Finished segmentation along the axial axis"

    def segment(self, file_path):
        """Main Segmentation Operation

        This function combines the segmentations from both axis to obtain the final result

        Args:
            file_path (str): Path to the desired input brain file

        Returns:
            filename (str): The file name of the outputted segmentation file.
        """

        self.state = "Starting evaluation"
        self.original = nib.load(file_path)

        self.volume_prediction = np.zeros((256, 33, 256, 256), dtype=np.half)

        with torch.no_grad():
            self._segment_over_one_axis(file_path, orientation="COR")
            self._segment_over_one_axis(file_path, orientation="AXI")
            # Take the class with maximum probability
            self.volume_prediction = np.argmax(self.volume_prediction, axis=1)
            self.volume_prediction = np.squeeze(self.volume_prediction)

            nifti_img = nib.Nifti1Image(self.volume_prediction, new_affine)
            to_save = undo_transform(nifti_img, self.original)

            if ".gz" in file_path:
                filename = file_path[:-7] + str('_segmented.nii.gz')
            else:
                filename = file_path[:-4] + str('_segmented.nii.gz')
            nib.save(to_save, filename)

            self.state = "Finished evaluation"

            # Segmentation is done so we clear the memory
            self.volume_prediction = 0
            return filename


def load_and_preprocess(file_path, orientation):
    """Load & Preprocess

    This function is composed of two other function calls: one that calls a function loading the data, and another which preprocesses the data to the required format.
    # TODO: Need to check if any more preprocessing would be required besides summing the tracts!

    Args:
        file_paths (list): List containing the input data and target labelled output data
        orientation (str): String detailing the current view (COR, SAG, AXL)

    Returns:
        volume (np.array): Array of training image data of data type dtype.
        header (class): 'nibabel.nifti1.Nifti1Header' class object, containing image metadata
        original (class): 'nibabel.nifti1.Nifti1Image' class object, containing the original input volume
    """

    original = nib.load(file_path)
    volume_nifty = transform(original)
    volume = volume_nifty.get_fdata()
    volume = (volume - np.min(volume)) / (np.max(volume) - np.min(volume))
    if orientation == "COR":
        volume = volume.transpose((2, 0, 1))
    elif orientation == "AXI":
        volume = volume.transpose((1, 2, 0))
    return volume


def transform(image):
    """Conformation Function

    This function takes a brain extracted image and conforms it to [256, 256, 256] and 1 mm^3 voxel size just like Freesurfer's mri_conform function

    Args:
        image (Nifti1Image): Input image to be conformed.

    Returns:
        transformed_image (Nifti1Image): Conformed image. 

    """

    shape = (256, 256, 256)
    # creating new image with the new affine and shape
    new_img = resample_img(image, new_affine, target_shape=shape)
    # change orientation
    orientation = nib.orientations.axcodes2ornt(
        nib.aff2axcodes(new_img.affine))
    target_orientation = np.array([[0., -1.], [2., -1.], [1., 1.]])
    transformation = nib.orientations.ornt_transform(
        orientation, target_orientation)
    data = new_img.get_fdata()
    data = np.rint(data / np.max(data) * 255)
    # Putting log correction back in. But estimating the magic number by fitting to some conformed brains.
    # These values are therefore empirical (potentially need to improve them, but better than hardcoded)
    var = np.var(data)
    magic_number = 0.15 + 0.0002874 * var + \
                   7.9317 / var - 2.986 / np.mean(data)
    scale = (np.max(data) - np.min(data))
    data = np.log2(1 + data.astype(float) / scale) * \
           scale * np.clip(magic_number, 0.9, 1.6)
    data = np.rint(np.clip(data, 0, 255))  # Ensure values do not go over 255
    # Continues as before from here
    data = data.astype(np.uint8)

    new_tran = nib.orientations.apply_orientation(data, transformation)
    transformed_image = nib.Nifti1Image(new_tran, new_affine)
    return transformed_image


def undo_transform(mask, original):
    """Undo transforation

    Function which reverts a previously performed transformation.

    Args:
        mask (Nifti1Image): Image to be reverted to a previous state
        original (Nifti1Image): The original model which serves as a reference

    Returns:
        new_mask (Nifti1Image): The reverted image

    """
    shape = original.get_data().shape
    new_mask = resample_img(mask, original.affine,
                            target_shape=shape, interpolation='nearest')
    # Adds a description to the nifti image

    new_mask.header["descrip"] = np.array(
        "Segmentation of " + str(original.header["db_name"])[2:-1], dtype='|S80')

    return new_mask
