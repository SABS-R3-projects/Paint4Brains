import os
import nibabel as nib
from nilearn.image import resample_img
import numpy as np
import torch
import csv
from fbs_runtime.application_context.PyQt5 import ApplicationContext

app = ApplicationContext()
coronal_model_path = app.get_resource("saved_models/finetuned_alldata_coronal.pth.tar")
axial_model_path = app.get_resource("saved_models/finetuned_alldata_axial.pth.tar")


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
    def __init__(self, device="cpu", coronal_model_path=coronal_model_path, axial_model_path=axial_model_path):
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
        """Segments given volume along one orientation

        Given the file_path and orientation it returns the probability of each voxel being in one of the
        33 possible classes.
        """

        volume = load_and_preprocess(file_path, orientation=orientation)
        volume = volume if len(volume.shape) == 4 else volume[:, np.newaxis, :, :]
        volume = torch.tensor(volume).type(torch.FloatTensor)

        if orientation == "COR":
            self.state = "Segmenting slices along the coronal axis"
            model = torch.load(self.coronal_model_path, map_location=torch.device(self.device))
        elif orientation == "AXI":
            self.state = "Segmenting slices along the axial axis"
            model = torch.load(self.axial_model_path, map_location=torch.device(self.device))
        model.eval()

        volume_pred = np.zeros((256, 33, 256, 256), dtype=np.half)
        for i in range(len(volume)):
            if not self.run:
                self.state = "Not running"
                self.completion = 0
                raise(Exception("Segmentation has been killed"))
                break
            self.completion = self.completion + 50 / 256
            batch_x = volume[i:i + 1]
            if self.cuda_available and self.device == "cuda":
                batch_x = batch_x.cuda(self.device)
            volume_pred[i] = model(batch_x).cpu().numpy().astype(np.half)

        if orientation == "COR":
            volume_pred = volume_pred.transpose((2, 1, 3, 0))
            self.state = "Finished segmentation along the coronal axis"
        elif orientation == "AXI":
            volume_pred = volume_pred.transpose((3, 1, 0, 2))
            self.state = "Finished segmentation along the axial axis"

        return volume_pred

    def segment(self, file_path):
        """Combines the segmentation from both axis to obtain the final result"""

        self.state = "Starting evaluation"
        self.original = nib.load(file_path)

        with torch.no_grad():
            volume_prediction_cor = self._segment_over_one_axis(file_path, orientation="COR")
            volume_prediction_axi = self._segment_over_one_axis(file_path, orientation="AXI")
            # Add the probabilities from both segmentations and take the maximum
            volume_prediction = np.argmax(volume_prediction_axi + volume_prediction_cor, axis=1)
            volume_prediction = np.squeeze(volume_prediction)

            nifti_img = nib.Nifti1Image(volume_prediction, new_affine)
            to_save = undo_transform(nifti_img, self.original)

            if ".gz" in file_path:
                filename = file_path[:-7] + str('_segmented.nii.gz')
            else:
                filename = file_path[:-4] + str('_segmented.nii.gz')
            nib.save(to_save, filename)

            self.state = "Finished evaluation"
            return filename


def load_and_preprocess(file_path, orientation):
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
    """Takes brain image and conforms it to [256, 256, 256]
    and 1 mm^3 voxel after doing some intensity normalization"""
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
