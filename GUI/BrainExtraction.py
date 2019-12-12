import nibabel as nb
from deepbrain import Extractor
import numpy as np

file = "segmented"
img = nb.load(file + ".nii").get_fdata()
ext = Extractor()#I made changes to extractor to beacause tensorflow has been updated
prob = ext.run(img) #Probabilities of brain tissue
mask2 = np.where(prob>0.3, 1, prob*0)#An outline of the extracted brain
brain_mask = img*mask2#Extracted brain
brain_mask = nb.Nifti1Image(brain_mask, affine=np.eye(4,4))
nb.save(brain_mask, "BrainExtracted_" + file + ".nii")


