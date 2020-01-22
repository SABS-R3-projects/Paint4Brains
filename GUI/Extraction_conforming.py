import os
import nibabel as nb
import nibabel as nib
import nilearn as nl
import numpy as np
from deepbrain import Extractor

# Changing directory to the Desktop where nii files are located
os.chdir('/home/sabs-r3/Desktop')
free_surfer = nib.load('80yearold_brain_fsl_bet_FS.nii')
no_bet = nib.load('77year.nii')


def extract(image):
    # Method to extract and realign the extracted image to the orientation of the original image
    new_affine = image.affine
    img = image.get_fdata()
    ext = Extractor()
    prob = ext.run(img)  # Returns an array with probabilities of where brain tissue should be
    mask2 = np.where(prob > 0.5, 1, prob * 0)  # Returns an outline of the extracted brain
    brain_mask = img * mask2  # Multiplies anything that is not brain tissue by a zero, returning an extracted brain
    brain_mask = nib.Nifti1Image(brain_mask, new_affine)
    brain_mask.set_header = image.header
    nb.save(brain_mask, "77BrainExtracted_deepBrain.nii")
    return brain_mask


def transform(image):
    """Takes brain extracted image and conforms it to [256, 256, 256]
    and 1 mm^3 voxel size just like Freesurfer's mri_conform function"""
    # setting voxel size and image dimensions
    new_zooms = (1, 1, 1)
    shape = (256, 256, 256)
    # setting affine for size and dimension
    # This is the affine that we get from FreeSurfer
    new_affine = np.array([[-1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.24474785e+02],
                           [0.00000000e+00, 1.26437587e-29, 1.00000012e+00, -1.04062988e+02],
                           [-6.46234854e-27, -1.00000012e+00, 0.00000000e+00, 1.44437317e+02],
                           [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    # creating new image with the new affine and shape
    new_img = nl.image.resample_img(image, new_affine, target_shape=shape)
    # change orientation
    orientation = nib.orientations.axcodes2ornt(nb.aff2axcodes(new_img.affine))
    target_orientation = np.array([[0., -1.], [2., -1.], [1., 1.]])
    transformation = nib.orientations.ornt_transform(orientation, target_orientation)
    data = new_img.get_data()
    new_tran = nib.orientations.apply_orientation(data, transformation)
    transformed_image = nib.Nifti1Image(new_tran, new_affine)
    return transformed_image


extracted_brain = extract(no_bet)
new_image = transform(extracted_brain)
new_image.set_header = free_surfer.header
nib.save(new_image, 'Segments_conformed.nii')
