import nibabel as nib
import os
import nilearn as nl

#Resamples the segmented mask so that it can be overlaid to the original  un-processed image
os.chdir('/home/sabs-r3/Desktop/')
mask = nib.load('segmented.nii.gz')
original = nib.load('MCI_M_77.nii')
dimensions = original.header['dim']
shape = original.get_data().shape
pixel_size = original.header['pixdim']
new_zooms = (pixel_size[1], pixel_size[2], pixel_size[3])
new_mask = nl.image.resample_img(mask, original.affine, target_shape=shape, interpolation='nearest')
nib.save(new_mask, 'Segmentated_to_Original_MRI.nii')