#Automatic brain extraction
#from nipype.interfaces.fsl import BET
import nibabel as nb
from deepbrain import Extractor
import numpy as np

#skullstrip = BET(in_file="80yearold.nii",
#                 out_file="80yearold_bet.nii.gz",
#                 mask=False, robust = True)
#res = skullstrip.run()

img = nb.load("80yearold.nii").get_fdata()
ext = Extractor()#I made changes to extractor to beacause tensorflow has been updated
prob = ext.run(img) #Probabilities of brain tissue
mask2 = np.where(prob>0.3, 1, prob*0)#An outline of the extracted brain
brain_mask = img*mask2#Extracted brain
#probabilities = nb.Nifti1Image(prob, affine=np.eye(4,4))
brain_mask = nb.Nifti1Image(brain_mask, affine=np.eye(4,4))
#nb.save(probabilities, 'Probabilities_DeepBrain_bet.nii')
nb.save(brain_mask, 'BrainExtracted_DeepBrain.nii')



