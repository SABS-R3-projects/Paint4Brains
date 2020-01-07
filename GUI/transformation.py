'''
Transform Nifti images to FreeSurfer standard with 1x1x1 voxel dimension

'''

import nilearn as nl
import nibabel as nb
from dipy.align.reslice import reslice
from dipy.data import get_fnames
import numpy as np

def transform(image):
    # setting voxel size and image dimensions
    new_zooms = (1,1,1)
    shape = (256,256,256)

    # setting affine for size and dimension
    new_affine = nb.volumeutils.shape_zoom_affine(shape, new_zooms, x_flip=True)

    # creating new image with the new affine and shape
    new_img = nl.image.resample_img(image,new_affine, target_shape=shape)

    #change orientation
    orientation = nb.orientations.axcodes2ornt(nb.aff2axcodes(new_img.affine))
    target_orientation = np.array([[0.,-1.],[1.,1.],[2.,1.]])
    transformation = nb.orientations.ornt_transform(orientation, target_orientation)
    data = new_img.get_data()
    new_tran = nb.orientations.apply_orientation(data,transformation)
    transformed_image = nb.Nifti1Image(new_tran, new_affine)

    return transformed_image




