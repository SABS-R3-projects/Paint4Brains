import SimpleITK as sitk
import os
import nibabel as nb
from dltk.io.preprocessing import whitening
from nipype.interfaces.image import Reorient
import numpy as np
#Change the directory to where the Nifti image is located
os.chdir('/home/sabs-r3/Desktop/')

#Changing the image intensity
img2 = sitk.ReadImage('80year.nii')
image_array = sitk.GetArrayFromImage(img2)
normalized_img = whitening(image_array)
normalized_img = nb.Nifti1Image(normalized_img, affine=np.eye(4,4))
nb.save(normalized_img,'Normalized_image.nii')

#orientation that can be applied:
          #('RAS' or 'RAI' or 'RPS' or 'RPI' or 'LAS' or 'LAI' or
          # 'LPS' or 'LPI' or 'RSA' or 'RSP' or 'RIA' or 'RIP' or 'LSA' or
          # 'LSP' or 'LIA' or 'LIP' or 'ARS' or 'ARI' or 'ALS' or 'ALI' or
          # 'PRS' or 'PRI' or 'PLS' or 'PLI' or 'ASR' or 'ASL' or 'AIR' or
          # 'AIL' or 'PSR' or 'PSL' or 'PIR' or 'PIL' or 'SRA' or 'SRP' or
          # 'SLA' or 'SLP' or 'IRA' or 'IRP' or 'ILA' or 'ILP' or 'SAR' or
          # 'SAL' or 'SPR' or 'SPL' or 'IAR' or 'IAL' or 'IPR' or 'IPL',
          # nipype default value: RAS)
reorient = Reorient(orientation='RAS')
reorient.inputs.in_file = 'Normalized_image.nii'
res = reorient.run()
#Get a matlab description file and a Nifti image
res.outputs.out_file


