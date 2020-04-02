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


class Segmenter:
    def __init__(self):
        self.state = "Not running"
        self.completion = 0

    def segment_default(self, brain_file_path, device="cpu"):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        coronal_model_path = current_directory + "/saved_models/finetuned_alldata_coronal.pth.tar"
        axial_model_path = current_directory + "/saved_models/finetuned_alldata_axial.pth.tar"
        return self.evaluate2view(coronal_model_path, axial_model_path, brain_file_path, device)

    def evaluate2view(self, coronal_model_path, axial_model_path, brain_file_path, device):
        self.state = "Starting evaluation"

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
                volume_prediction_cor = self._segment_vol(file_path, model1, "COR",
                                                     cuda_available,
                                                     device)
                volume_prediction_axi = self._segment_vol(file_path, model2, "AXI",
                                                      cuda_available,
                                                      device)
                volume_prediction = np.argmax(volume_prediction_axi + volume_prediction_cor,
                                              axis=1)
                volume_prediction = np.squeeze(volume_prediction)

                # volume_prediction, header, original = load_and_preprocess(file_path, "AXI")    # For debugging
                # volume_prediction = np.transpose(volume_prediction, (2, 0, 1))   # For debugging

                nifti_img = nib.Nifti1Image(volume_prediction, new_affine)
                # ~~~~~~~~~~~~~~~~~ HERE WE CAN DO THE INVERSE TRANSFORM ~~~~~~~~~~~~~~~~~~~~
                to_save = undo_transform(nifti_img, self.original)
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if ".gz" in file_path:
                    filename = file_path[:-7] + str('_segmented.nii.gz')
                else:
                    filename = file_path[:-4] + str('_segmented.nii.gz')
                nib.save(to_save, filename)

                self.state = "Finished evaluation"
                return filename

            except FileNotFoundError as e:
                print("Error in reading the file ...")
                raise e

    def _segment_vol(self, file_path, model, orientation, cuda_available, device):
        volume, self.original = load_and_preprocess(file_path, orientation=orientation)

        volume = volume if len(volume.shape) == 4 else volume[:, np.newaxis, :, :]
        volume = torch.tensor(volume).type(torch.FloatTensor)

        if orientation == "COR":
            self.state = "Segmenting slices along the coronal axis"
        elif orientation == "AXI":
            self.state = "Segmenting slices along the axial axis"

        volume_pred = np.zeros((256, 33, 256, 256), dtype=np.half)
        for i in range(0, len(volume)):
            self.completion = i / 256
            batch_x = volume[i:i + 1]
            if cuda_available and device == "cuda":
                batch_x = batch_x.cuda(device)
            # _, batch_output = torch.max(out, dim=1)
            volume_pred[i] = model(batch_x).cpu().numpy().astype(np.half)

        if orientation == "COR":
            volume_pred = volume_pred.transpose((2, 1, 3, 0))
            self.state = "Finished segmentation along the coronal axis"
        elif orientation == "AXI":
            volume_pred = volume_pred.transpose((3, 1, 0, 2))
            self.state = "Finished segmentation along the axial axis"

        return volume_pred


def load_and_preprocess(file_path, orientation):
    original = nib.load(file_path)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~ HERE WE CAN DO PREPROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volume_nifty = transform(original)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volume = volume_nifty.get_fdata()
    volume = (volume - np.min(volume)) / (np.max(volume) - np.min(volume))
    if orientation == "COR":
        volume = volume.transpose((2, 0, 1))
    elif orientation == "AXI":
        volume = volume.transpose((1, 2, 0))
    return volume, original


def transform(image):
    """Takes brain extracted image and conforms it to [256, 256, 256]
    and 1 mm^3 voxel size just like Freesurfer's mri_conform function"""
    shape = (256, 256, 256)
    # creating new image with the new affine and shape
    new_img = resample_img(image, new_affine, target_shape=shape)
    # change orientation
    orientation = nib.orientations.axcodes2ornt(nib.aff2axcodes(new_img.affine))
    target_orientation = np.array([[0., -1.], [2., -1.], [1., 1.]])
    transformation = nib.orientations.ornt_transform(orientation, target_orientation)
    data = new_img.get_fdata()
    data = np.rint(data / np.max(data) * 255)
    # Putting log correction back in. But estimating the magic number by fitting to some conformed brains.
    # These values are therefore empirical (potentially need to improve them, but better than hardcoded)
    var = np.var(data)
    magic_number = 0.15 + 0.0002874 * var + 7.9317 / var - 2.986 / np.mean(data)
    scale = (np.max(data) - np.min(data))
    data = np.log2(1 + data.astype(float) / scale) * scale * np.clip(magic_number, 0.9, 1.6)
    data = np.rint(np.clip(data, 0, 255))  # Ensure values do not go over 255
    # Continues as before from here
    data = data.astype(np.uint8)

    new_tran = nib.orientations.apply_orientation(data, transformation)
    transformed_image = nib.Nifti1Image(new_tran, new_affine)
    return transformed_image


def undo_transform(mask, original):
    shape = original.get_data().shape
    new_mask = resample_img(mask, original.affine, target_shape=shape, interpolation='nearest')
    # Adds a description to the nifti image
    new_mask.header["descrip"] = np.array("Segmentation of " + str(original.header["db_name"])[2:-1], dtype='|S80')
    return new_mask
