import nibabel as nib
import os
import numpy as np
os.chdir('/home/sabs-r3/Desktop')
#Takes in the segmented mask from QuickNat to reorient it so that it can be overlaid with the original preprocessed mri image
orig_image = nib.load('MCI_M_77_ItaiPipe.nii.nii.gz')
orig_image = orig_image.get_fdata()
data = np.rint(orig_image / np.max(orig_image) * 255)
data = data.astype(np.uint8)
new_affine = np.array([[-1.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.24474785e+02],
                      [0.00000000e+00, 1.26437587e-29, 1.00000012e+00, -1.04062988e+02],
                      [-6.46234854e-27, -1.00000012e+00, 0.00000000e+00, 1.44437317e+02],
                       [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
#Affine to use next time for preprocessing
#new_affine = np.array([[-1, 0, 0, 120],
                    #  [0, 0, 1, -100],
                    #  [0, -1, 0, 140],
                    #  [0, 0, 0, 1]])

transformed_image = nib.Nifti1Image(data, new_affine)
nib.save(transformed_image, 'Final_SegmentationADNI_4.nii')
