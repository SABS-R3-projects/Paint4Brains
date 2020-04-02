"""Paint4Brains Segmented

This file contains the relevant functions for producing the segmented labeled brains, a core function of the Paint4Brains Software.
The functions and methods in this file were extracted from the several files associated with the original QuickNAT implementation.

Attributes:
    label_name (list): List of all labels correponding to the different regions that QuickNAT is able to segment.
    new_affine (np.array): Homogenous affine giving relationship between voxel coordinates and world coordinates for the segmneted files.

Usage:
    To use this module, import it and instantiate is as you wish:

        from Paint4Brains.Segmenter import function_name
        segmented_filename = function_name(parameters)
"""

import os
import nibabel as nib
from nilearn.image import resample_img
import numpy as np
import torch
import csv

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


def segment_default(brain_file_path, device="cpu"):
    """Function setting up the segmentation operation

    This function loads the current directory, loads the relevant models for the coronal and axial paths, defines the directory for saving the ouput volume and then calls the segmentation function.

    Args:
        brain_file_path (str): Path to the desired input brain file
        device (int/str): Device type used for training (int - GPU id, str- CPU)

    Returns:
        str: filename of the ouputed segmented volume
    """

    current_directory = os.path.dirname(os.path.realpath(__file__))
    coronal_model_path = current_directory + \
        "/saved_models/finetuned_alldata_coronal.pth.tar"
    axial_model_path = current_directory + \
        "/saved_models/finetuned_alldata_axial.pth.tar"
    save_predictions_dir = "outputs"
    return evaluate2view(coronal_model_path, axial_model_path, brain_file_path, save_predictions_dir, device)


def evaluate2view(coronal_model_path, axial_model_path, brain_file_path, prediction_path, device):
    """Run Segmentation operation

    This function runs the segmentation operation.
    This saves the segmentation files at nifti files in the destination folder.

    Args:
        coronal_model_path (str): Path to the pre-trained coronal QuickNAT model
        axial_model_path (str): Path to the pre-trained axial QuickNAT model
        brain_file_path (str): Path to the desired input brain file
        prediction_path (str): Path to the desired output segmented file
        device (int/str): Device type used for training (int - GPU id, str- CPU)

    Returns:
        str: filename of the ouputed segmented volume
    """
    print("**Starting evaluation**")

    file_path = brain_file_path
    cuda_available = torch.cuda.is_available()

    if type(device) == int:
        # if CUDA available, follow through, else warn and fallback to CPU
        if cuda_available:
            model1 = torch.load(coronal_model_path)
            model2 = torch.load(axial_model_path)

            torch.cuda.empty_cache()
            model1.cuda(device)
            model2.cuda(device)
        else:
            log.warning(
                'CUDA is not available, trying with CPU.' +
                'This can take much longer (> 1 hour). Cancel and ' +
                'investigate if this behavior is not desired.'
            )

    if (type(device) == str) or not cuda_available:
        model1 = torch.load(
            coronal_model_path,
            map_location=torch.device(device)
        )
        model2 = torch.load(
            axial_model_path,
            map_location=torch.device(device)
        )

    model1.eval()
    model2.eval()

    with torch.no_grad():
        try:
            volume_prediction_cor, header, original = _segment_vol(file_path, model1, "COR",
                                                                   cuda_available,
                                                                   device)
            volume_prediction_axi, header, original = _segment_vol(file_path, model2, "AXI",
                                                                   cuda_available,
                                                                   device)
            volume_prediction = np.argmax(volume_prediction_axi + volume_prediction_cor,
                                          axis=1)
            volume_prediction = np.squeeze(volume_prediction)

            # volume_prediction, header, original = load_and_preprocess(file_path, "AXI")    # For debugging
            # volume_prediction = np.transpose(volume_prediction, (2, 0, 1))   # For debugging

            nifti_img = nib.Nifti1Image(volume_prediction, new_affine)
            # ~~~~~~~~~~~~~~~~~ HERE WE CAN DO THE INVERSE TRANSFORM ~~~~~~~~~~~~~~~~~~~~
            to_save = undo_transform(nifti_img, original)
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if ".gz" in file_path:
                filename = file_path[:-7] + str('_segmented.nii.gz')
            else:
                filename = file_path[:-4] + str('_segmented.nii.gz')
            nib.save(to_save, filename)

            print("**Finished evaluation**")
            return filename

        except FileNotFoundError as e:
            print("Error in reading the file ...")
            raise (e)


def _segment_vol(file_path, model, orientation, cuda_available, device):
    """Forward Segmentation Pass

    This function loads a volume for segmentation, preprocesses it and then performs a forward pass through the model.

    Args:
        file_path (str): Path to the desired input brain file
        model (class): QuickNAT model class
        orientation (str): String indicating the input orientation of the file
        cuda_available (bool): Flag indicating if a cuda-enabled GPU is available
        device (int/str): Device type used for training (int - GPU id, str- CPU)

    Returns:
        volume_pred (np.array): Array containing the predicted labelled data volume
        header (class): 'nibabel.nifti1.Nifti1Header' class object, containing volume metadata
        original (class): 'nibabel.nifti1.Nifti1Image' class object, containing the original input volume
    """

    volume, header, original = load_and_preprocess(
        file_path, orientation=orientation)

    volume = volume if len(volume.shape) == 4 else volume[:, np.newaxis, :, :]
    volume = torch.tensor(volume).type(torch.FloatTensor)

    volume_pred = np.zeros((256, 33, 256, 256), dtype=np.half)
    for i in range(0, len(volume)):
        print(i)
        batch_x = volume[i:i + 1]
        if cuda_available and device == "cuda":
            batch_x = batch_x.cuda(device)
        # _, batch_output = torch.max(out, dim=1)
        volume_pred[i] = model(batch_x).cpu().numpy().astype(np.half)

    if orientation == "COR":
        volume_pred = volume_pred.transpose((2, 1, 3, 0))
    elif orientation == "AXI":
        volume_pred = volume_pred.transpose((3, 1, 0, 2))

    return volume_pred, header, original


def load_and_preprocess(file_path, orientation):
    """Load & Preprocess

    This function is composed of two other function calls: one that calls a function loading the data, and another which preprocesses the data to the required format.
    # TODO: Need to check if any more proprocessing would be required besides summing the tracts!

    Args:
        file_paths (list): List containing the input data and target labelled output data
        orientation (str): String detailing the current view (COR, SAG, AXL)

    Returns:
        volume (np.array): Array of training image data of data type dtype.
        header (class): 'nibabel.nifti1.Nifti1Header' class object, containing image metadata
        original (class): 'nibabel.nifti1.Nifti1Image' class object, containing the original input volume
    """

    original = nib.load(file_path)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~ HERE WE CAN DO PREPROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volume_nifty = transform(original)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    header = volume_nifty.header
    volume = volume_nifty.get_fdata()
    volume = (volume - np.min(volume)) / (np.max(volume) - np.min(volume))
    if orientation == "COR":
        volume = volume.transpose((2, 0, 1))
    elif orientation == "AXI":
        volume = volume.transpose((1, 2, 0))
    return volume, header, original


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
