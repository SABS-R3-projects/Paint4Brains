import nibabel as nib
import os
import numpy as np
import nilearn as nl

#Trying to resample the segmentation to the original image that has not been preprocessed
os.chdir('/home/sabs-r3/Desktop')
mask = nib.load('77yearConf.nii.nii.gz')
original = nib.load('77year.nii')
dimensions = original.header['dim']
shape = [dimensions[1], dimensions[2], dimensions[3]]
pixel_size = original.header['pixdim']
new_zooms = (pixel_size[1], pixel_size[2], pixel_size[3])
target_affine = nib.volumeutils.shape_zoom_affine(shape, new_zooms)
new_mask = nl.image.resample_img(mask, target_affine, target_shape=shape, interpolation='nearest')


orientation = nib.orientations.axcodes2ornt(nib.aff2axcodes(new_mask.affine))
target_orientation = nib.orientations.axcodes2ornt(nib.aff2axcodes(target_affine))
transformation = nib.orientations.ornt_transform(orientation, target_orientation)
data = new_mask.get_fdata()
new_affine = target_affine
new_tran = nib.orientations.apply_orientation(data, transformation)
transformed_image = nib.Nifti1Image(new_tran, new_affine)
nib.save(transformed_image, 'Segmentated_to_Original_MRI.nii')