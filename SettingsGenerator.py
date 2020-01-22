import configparser
import os

def get_current_directory():

    """
    This function returns the full path of the directory where the current script is contained in. This will be later relevant, for generating the settings_eval.ini function.

    Args:
        None

    Raises:
        None
    
    Returns:
        dir_path (str): string containing the full path where the current script is contained in.

    """

    # First, we want to get the current directory of where we currently are. This will be relevant later.
    dir_path = os.path.dirname(os.path.realpath(__file__))

    return dir_path

def read_original_configurator():

    """
    This function reads the original configuration file and returns all the values contained within in.

    Args:
        None

    Raises:
        None
    
    Returns:
        setting_dictionary (dict): dictionary containing the original configuration file information

    """

    directory_path = get_current_directory()

    config = configparser.ConfigParser()

    config._interpolation = configparser.ExtendedInterpolation()

    config.read(directory_path+'/settings_eval_original.ini')
    
    sections = config.sections()

    settings_dictionary = {}

    options = config.options(sections[0])

    for option in options:
        try:
            settings_dictionary[option] = config[sections[0]][option]
            if settings_dictionary[option] == -1:
                DebugPring("skip: %s" % option)
        except:
            print("Exception on %s!" % option)
            settings_dictionary[option] = None

    return sections[0], settings_dictionary

def parser_configurator():
    """
    This function prints out the current settings, asks for a user input to update the settings and creates a new settings file.

    Args:
        None

    Raises:
        None
    
    Returns:
        dir_path (str): string containing the full path where the current script is contained in.

    This function will need to be changed once the GUI settings window is created! 

    """

    directory_path = get_current_directory()

    section_name, settings_dictionary = read_original_configurator()

    config = configparser.ConfigParser()

    inputs = []

    for key in settings_dictionary:
        if key == 'device':
            print("Provide CPU or ID of GPU (0 or 1) you want to excecute your code, or press Enter to leave default")
            data_input = input("Your input:")
            if data_input == "":
                single_input = settings_dictionary[key]
            else:
                single_input = data_input
        elif key == 'coronal_model_path':
            single_input = settings_dictionary[key]
        elif key == 'axial_model_path':
            single_input = settings_dictionary[key]
        elif key == 'data_dir':
            single_input = '"'+directory_path+'/quickNAT_pythorch/data_input'+'"'
        elif key == 'directory_struct':
            print("Valid options for data directory structure are >> FS <<  or >> Linear <<. If you input data directory is similar to FreeSurfer, i.e. data_dir/<Data_id>/mri/orig.mgz then use >> FS <<. If the entries are data_dir/<Data_id> use >> Linear <<. To leave at default, press Enter")
            data_input = input("Provide information about input directory structure: ")
            if data_input == "":
                single_input = settings_dictionary[key]
            else:
                single_input = data_input
        elif key == 'volumes_txt_file':
            single_input = settings_dictionary[key]
        elif key == 'batch_size':
            single_input = settings_dictionary[key]
        elif key == 'save_predictions_dir':
            single_input = '"'+directory_path+'/quickNAT_pythorch/output_file'+'"'
        elif key == 'view_agg':
            single_input = settings_dictionary[key]
        elif key == 'estimate_uncertainty':
            single_input = settings_dictionary[key]
        elif key == 'mc_samples':
            single_input = settings_dictionary[key]

        inputs.append(str(single_input))
    
    
    cfgfile = open("settings_eval.ini",'w')
    config.add_section(section_name)

    for idx, key in enumerate(settings_dictionary):
        config.set(section_name, key ,inputs[idx])

    config.write(cfgfile)
    cfgfile.close()

if __name__=='__main__':

    parser_configurator()