import os
import nibabel as nib
import nilearn as nl
import numpy as np
import torch
import csv
from skimage import exposure


def segment_default(brain_file_path, device="CPU"):
    coronal_model_path = "saved_models/finetuned_alldata_coronal.pth.tar"
    axial_model_path = "saved_models/finetuned_alldata_axial.pth.tar"
    batch_size = 1
    save_predictions_dir = "output_file"
    label_names = ["vol_ID", "Background", "Left WM", "Left Cortex", "Left Lateral ventricle", "Left Inf LatVentricle",
                   "Left Cerebellum WM", "Left Cerebellum Cortex", "Left Thalamus", "Left Caudate", "Left Putamen",
                   "Left Pallidum", "3rd Ventricle", "4th Ventricle", "Brain Stem", "Left Hippocampus", "Left Amygdala",
                   "CSF (Cranial)", "Left Accumbens", "Left Ventral DC", "Right WM", "Right Cortex",
                   "Right Lateral Ventricle", "Right Inf LatVentricle", "Right Cerebellum WM",
                   "Right Cerebellum Cortex", "Right Thalamus", "Right Caudate", "Right Putamen", "Right Pallidum",
                   "Right Hippocampus", "Right Amygdala", "Right Accumbens", "Right Ventral DC"]
    evaluate2view(coronal_model_path, axial_model_path, brain_file_path, save_predictions_dir, device, batch_size,
                  label_names)


def evaluate2view(coronal_model_path, axial_model_path, brain_file_path, prediction_path, device, batch_size,
                  label_names):
    print("**Starting evaluation**")

    file_paths = [brain_file_path]

    model1 = torch.load(coronal_model_path, map_location=torch.device('cpu'))

    model2 = torch.load(axial_model_path, map_location=torch.device('cpu'))

    cuda_available = torch.cuda.is_available()
    if cuda_available:
        torch.cuda.empty_cache()
        model1.cuda(device)
        model2.cuda(device)

    model1.eval()
    model2.eval()

    create_if_not(prediction_path)
    print("Evaluating now...")

    with torch.no_grad():
        volume_dict_list = []
        for vol_idx, file_path in enumerate(file_paths):
            try:
                volume_prediction_cor, _, header, original = _segment_vol(file_path, model1, "COR", batch_size,
                                                                cuda_available,
                                                                device)
                volume_prediction_axi, _, header, original = _segment_vol(file_path, model2, "AXI", batch_size,
                                                                cuda_available,
                                                                device)
                _, volume_prediction = torch.max(volume_prediction_axi + volume_prediction_cor, dim=1)
                volume_prediction = (volume_prediction.cpu().numpy()).astype('float32')
                volume_prediction = np.squeeze(volume_prediction)
                nifti_img = nib.Nifti1Image(volume_prediction, np.eye(4), header=header)
                print("Processed: " + volumes_to_use[vol_idx] + " " + str(vol_idx + 1) + " out of " + str(
                    len(file_paths)))
                # ~~~~~~~~~~~~~~~~~ HERE WE CAN DO THE INVERSE TRANSFORM ~~~~~~~~~~~~~~~~~~~~
                to_save = undo_transform(nifti_img, original)
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                nib.save(to_save, os.path.join(prediction_path, volumes_to_use[vol_idx][:-4] + str('_segmented.nii.gz')))

                per_volume_dict = compute_volume(volume_prediction, label_names, volumes_to_use[vol_idx])
                volume_dict_list.append(per_volume_dict)

            except FileNotFoundError:
                print("Error in reading the file ...")
            except Exception as exp:
                import logging
                logging.getLogger(__name__).exception(exp)
                # print("Other kind o error!")

        _write_csv_table('volume_estimates.csv', prediction_path, volume_dict_list, label_names)

    print("DONE")


def _write_csv_table(name, prediction_path, dict_list, label_names):
    file_name = name
    file_path = os.path.join(prediction_path, file_name)
    # Save volume_dict as csv file in the prediction_path
    with open(file_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=label_names)
        writer.writeheader()

        for data in dict_list:
            writer.writerow(data)


def _segment_vol(file_path, model, orientation, batch_size, cuda_available, device):
    volume, header, original = load_and_preprocess(file_path, orientation=orientation)

    volume = volume if len(volume.shape) == 4 else volume[:, np.newaxis, :, :]
    volume = torch.tensor(volume).type(torch.FloatTensor)

    volume_pred = []
    for i in range(0, len(volume), batch_size):
        batch_x = volume[i: i + batch_size]
        if cuda_available:
            batch_x = batch_x.cuda(device)
        out = model(batch_x)
        # _, batch_output = torch.max(out, dim=1)
        volume_pred.append(out)

    volume_pred = torch.cat(volume_pred)
    _, volume_prediction = torch.max(volume_pred, dim=1)

    volume_prediction = (volume_prediction.cpu().numpy()).astype('float32')
    volume_prediction = np.squeeze(volume_prediction)
    if orientation == "COR":
        volume_prediction = volume_prediction.transpose((1, 2, 0))
        volume_pred = volume_pred.permute((2, 1, 3, 0))
    elif orientation == "AXI":
        volume_prediction = volume_prediction.transpose((2, 0, 1))
        volume_pred = volume_pred.permute((3, 1, 0, 2))

    return volume_pred, volume_prediction, header, original


def load_and_preprocess(file_path, orientation):
    original = nib.load(file_path)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~ HERE WE CAN DO PREPROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volume_nifty = transform(original)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    header = volume_nifty.header
    volume = volume_nifty.get_fdata()
    volume = (volume - np.min(volume)) / (np.max(volume) - np.min(volume))
    if orientation == "COR":
        volume = volume.transpose((2, 0, 1))
    elif orientation == "AXI":
        volume = volume.transpose((1, 2, 0))
    return volume, header, original


def create_if_not(path):
    """
    Creates a folder at the given path if one doesnt exist before
    ===

    :param path: destination to check for existense
    :return: None
    """
    if not os.path.exists(path):
        os.makedirs(path)


def transform(image):
    """Takes brain extracted image and conforms it to [256, 256, 256]
    and 1 mm^3 voxel size just like Freesurfer's mri_conform function"""
    shape = (256, 256, 256)
    # This is the affine that we get from FreeSurfer
    new_affine = np.array([[-1, 0., 0, 128],
                           [0., 0., 1, -128],
                           [0., -1, 0, 128],
                           [0., 0., 0, 1]])

    # creating new image with the new affine and shape
    new_img = nl.image.resample_img(image, new_affine, target_shape=shape)
    # change orientation
    orientation = nib.orientations.axcodes2ornt(nib.aff2axcodes(new_img.affine))
    target_orientation = np.array([[0., -1.], [2., -1.], [1., 1.]])
    transformation = nib.orientations.ornt_transform(orientation, target_orientation)
    data = new_img.get_fdata()
    data = np.rint(data / np.max(data) * 255)
    data = data.astype(np.uint8)

    data = exposure.adjust_log(data, 1.3)

    new_tran = nib.orientations.apply_orientation(data, transformation)
    transformed_image = nib.Nifti1Image(new_tran, new_affine)
    return transformed_image


def undo_transform(mask, original):
    shape = original.get_data().shape
    new_mask = nl.image.resample_img(mask, original.affine, target_shape=shape, interpolation='nearest')
    # Adds a description to the nifti image
    new_mask.header["descrip"] = np.array("Segmentation of " + str(original.header["db_name"])[2:-1], dtype='|S80')
    return new_mask


#segment_default("/home/sabs-r3/Desktop/quickNAT_pytorch/brains/MCI_F_83_1_conformed.nii")
