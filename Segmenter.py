import os
import nibabel as nib
import nilearn as nl
import numpy as np
import torch
import csv

label_names = ["vol_ID", "Background", "Left WM", "Left Cortex", "Left Lateral ventricle", "Left Inf LatVentricle",
               "Left Cerebellum WM", "Left Cerebellum Cortex", "Left Thalamus", "Left Caudate", "Left Putamen",
               "Left Pallidum", "3rd Ventricle", "4th Ventricle", "Brain Stem", "Left Hippocampus", "Left Amygdala",
               "CSF (Cranial)", "Left Accumbens", "Left Ventral DC", "Right WM", "Right Cortex",
               "Right Lateral Ventricle", "Right Inf LatVentricle", "Right Cerebellum WM",
               "Right Cerebellum Cortex", "Right Thalamus", "Right Caudate", "Right Putamen", "Right Pallidum",
               "Right Hippocampus", "Right Amygdala", "Right Accumbens", "Right Ventral DC"]

new_affine = np.array([[-1, 0., 0, 128],
                       [0., 0., 1, -128],
                       [0., -1, 0, 128],
                       [0., 0., 0, 1]])

def segment_all_in_directory(directory, device = "cpu", volume_estimates = True):
    """device should be "cuda" if you want to run on GPU"""
    brain_files = [x for x in os.listdir(directory) if (x[-4:] == ".nii" or x[-7:] == ".nii.gz") and "segmented" not in x]

    for file in brain_files:
        print("Segmenting " + file)
        result = segment_default(file, device)
        if volume_estimates:
            compute_volume(result)





def segment_default(brain_file_path, device="cpu"):
    current_directory = os.path.dirname(os.path.realpath(__file__))
    coronal_model_path = current_directory + "/saved_models/finetuned_alldata_coronal.pth.tar"
    axial_model_path = current_directory + "/saved_models/finetuned_alldata_axial.pth.tar"
    batch_size = 1
    return evaluate2view(coronal_model_path, axial_model_path, brain_file_path, device, batch_size)


def compute_volume(brain_file_path):

    volume_nifty = nib.load(brain_file_path)
    header = volume_nifty.header
    volume = volume_nifty.get_data()
    sizes = header.get_zooms()[:3]

    size_correction = np.prod(sizes)
    labels, number_of_pixels = np.unique(volume, return_counts = True)
    volume_dict = {label_names[i+1]: size_correction*number_of_pixels[i] for i in labels}
    volume_dict[label_names[0]] = os.path.basename(brain_file_path)
    csv_file_name = 'volume_estimates.csv'
    with open(csv_file_name, 'a+') as f:
        writer = csv.DictWriter(f, fieldnames=label_names)
        if os.stat(csv_file_name).st_size == 0:
            writer.writeheader()
        writer.writerow(volume_dict)



def evaluate2view(coronal_model_path, axial_model_path, brain_file_path,device, batch_size):
    print("**Starting evaluation**")

    file_path = brain_file_path
    cuda_available = torch.cuda.is_available()

    if type(device) == int:
        # if CUDA available, follow through, else warn and fallback to CPU
        if cuda_available:
            model1 = torch.load(coronal_model_path)
            model2 = torch.load(axial_model_path)

            torch.cuda.empty_cache()
            model1.cuda(device)
            model2.cuda(device)
        else:
            log.warning(
                'CUDA is not available, trying with CPU.' + \
                'This can take much longer (> 1 hour). Cancel and ' + \
                'investigate if this behavior is not desired.'
            )

    if (type(device) == str) or not cuda_available:
        model1 = torch.load(
            coronal_model_path,
            map_location=torch.device(device)
        )
        model2 = torch.load(
            axial_model_path,
            map_location=torch.device(device)
        )

    model1.eval()
    model2.eval()

    with torch.no_grad():
        try:
            volume_prediction_cor, header, original = _segment_vol(file_path, model1, "COR", batch_size,
                                                                      cuda_available,
                                                                      device)
            volume_prediction_axi, header, original = _segment_vol(file_path, model2, "AXI", batch_size,
                                                                      cuda_available,
                                                                      device)
            volume_prediction = np.argmax(volume_prediction_axi + volume_prediction_cor, axis=1)
            volume_prediction = np.squeeze(volume_prediction)

            nifti_img = nib.Nifti1Image(volume_prediction, new_affine)
            # ~~~~~~~~~~~~~~~~~ HERE WE CAN DO THE INVERSE TRANSFORM ~~~~~~~~~~~~~~~~~~~~
            to_save = undo_transform(nifti_img, original)
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if ".gz" in file_path:
                filename = file_path[:-7] + str('_segmented.nii.gz')
            else:
                filename = file_path[:-4] + str('_segmented.nii.gz')
            nib.save(to_save, filename)

            print("**Finished evaluation**")
            return filename

        except FileNotFoundError:
            print("Error in reading the file ...")
        except Exception as exp:
            import logging
            logging.getLogger(__name__).exception(exp)
            # print("Other kind o error!")


def _segment_vol(file_path, model, orientation, batch_size, cuda_available, device):
    volume, header, original = load_and_preprocess(file_path, orientation=orientation)

    volume = volume if len(volume.shape) == 4 else volume[:, np.newaxis, :, :]
    volume = torch.tensor(volume).type(torch.FloatTensor)

    volume_pred = np.zeros((256, 33, 256, 256), dtype=np.half)
    for i in range(0, len(volume), batch_size):
        batch_x = volume[i: i + 1]
        if cuda_available:
            batch_x = batch_x.cuda(device)
        out = model(batch_x)
        # _, batch_output = torch.max(out, dim=1)
        volume_pred[i] = out.cpu().numpy().astype(np.half)

    if orientation == "COR":
        volume_pred = volume_pred.transpose((2, 1, 3, 0))
    elif orientation == "AXI":
        volume_pred = volume_pred.transpose((3, 1, 0, 2))

    return volume_pred, header, original


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


def transform(image):
    """Takes brain extracted image and conforms it to [256, 256, 256]
    and 1 mm^3 voxel size just like Freesurfer's mri_conform function"""
    shape = (256, 256, 256)
    # creating new image with the new affine and shape
    new_img = nl.image.resample_img(image, new_affine, target_shape=shape)
    # change orientation
    orientation = nib.orientations.axcodes2ornt(nib.aff2axcodes(new_img.affine))
    target_orientation = np.array([[0., -1.], [2., -1.], [1., 1.]])
    transformation = nib.orientations.ornt_transform(orientation, target_orientation)
    data = new_img.get_fdata()
    data = np.rint(data / np.max(data) * 255)
    # Putting log correction back in. But estimating the magic number by fitting to some conformed brains.
    # These values are therefore empirical (potentially need to improve them, but better than hardcoded)
    var = np.var(data)
    magic_number = 0.15 + 0.0002874 * var + 7.9317 / var - 2.986 / np.mean(data)
    scale = (np.max(data) - np.min(data))
    data = np.log2(1 + data.astype(float) / scale) * scale * np.clip(magic_number, 0.9, 1.6)
    data = np.rint(np.clip(data, 0, 255))  # Ensure values do not go over 255
    # Continues as before from here
    data = data.astype(np.uint8)

    new_tran = nib.orientations.apply_orientation(data, transformation)
    transformed_image = nib.Nifti1Image(new_tran, new_affine)
    return transformed_image


def undo_transform(mask, original):
    shape = original.get_data().shape
    new_mask = nl.image.resample_img(mask, original.affine, target_shape=shape, interpolation='nearest')
    # Adds a description to the nifti image
    new_mask.header["descrip"] = np.array("Segmentation of " + str(original.header["db_name"])[2:-1], dtype='|S80')
    return new_mask

