from utils.evaluator import evaluate2view


def segment_default(brain_file_path, device="CPU"):
    coronal_model_path = "saved_models/finetuned_alldata_coronal.pth.tar"
    axial_model_path = "saved_models/finetuned_alldata_axial.pth.tar"
    garbage = "not_needed"
    batch_size = 1
    save_predictions_dir = "output_file"
    label_names = ["vol_ID", "Background", "Left WM", "Left Cortex", "Left Lateral ventricle", "Left Inf LatVentricle",
                   "Left Cerebellum WM", "Left Cerebellum Cortex", "Left Thalamus", "Left Caudate", "Left Putamen",
                   "Left Pallidum", "3rd Ventricle", "4th Ventricle", "Brain Stem", "Left Hippocampus", "Left Amygdala",
                   "CSF (Cranial)", "Left Accumbens", "Left Ventral DC", "Right WM", "Right Cortex",
                   "Right Lateral Ventricle", "Right Inf LatVentricle", "Right Cerebellum WM",
                   "Right Cerebellum Cortex", "Right Thalamus", "Right Caudate", "Right Putamen", "Right Pallidum",
                   "Right Hippocampus", "Right Amygdala", "Right Accumbens", "Right Ventral DC"]
    evaluate2view(coronal_model_path, axial_model_path, garbage, garbage, device, save_predictions_dir, batch_size,
                  label_names, garbage, brain_file_path=brain_file_path)


segment_default("/home/sabs-r3/Desktop/quickNAT_pytorch/brains/MCI_F_83_1_conformed.nii")
