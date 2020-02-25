import os
from fbs_runtime.application_context.PyQt5 import ApplicationContext

app = ApplicationContext()
executable_dir = app.get_resource('FS')
save_folder = app.get_resource('temporary')


def prepare(filename):
    preprocessed = filename
    converted = save_folder + "/conformed.nii"

    os.environ["FREESURFER_HOME"] = executable_dir
    os.system(executable_dir + "/mri_convert.bin --conform " + preprocessed + " " + converted)

    return converted
