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
    This function reads the original configuration file anre returns all the values contained within in.

    Args:
        None

    Raises:
        None
    
    Returns:
        dir_path (str): string containing the full path where the current script is contained in.

    """

    directory_path = get_current_directory()

    config = configparser.ConfigParser()

    config._interpolation = configparser.ExtendedInterpolation()

    config.read(directory_path+'/settings_eval_original.ini')
    
    sections = config.sections()

    settings_dictionary = {}

    options = config.options(sections[0])

    print("Sections:", sections)
    print("Options:", options)

    for option in options:
        print(option)
        print(config[sections][option])

    # for option in options:
    #     settings_dictionary[option] = config.get(sections,option)
        # try:
        #     settings_dictionary[option] = config.get(section,option)
        #     if settings_dictionary[option] == -1:
        #         DebugPring("skip: %s" % option)
        # except:
        #     print("Exception on %s!" % option)
        #     settings_dictionary[option] = None

    # print(settings_dictionary)

    print(options)
    print(config.sections())

def parser_configurator():
    """
    This function returns the full path of the directory where the current script is contained in. This will be later relevant, for generating the settings_eval.ini function.

    Args:
        None

    Raises:
        None
    
    Returns:
        dir_path (str): string containing the full path where the current script is contained in.

    """

    directory_path = get_current_directory()

    config = configparser.ConfigParser()

    config['DEFAULT'] = {
        'ServerAliveInterval': '45',
        'Compression': 'yes',
        'CompressionLevel': '9'
        }
    config['bitbucket.org'] = {}
    config['bitbucket.org']['User'] = 'hg'
    config['topsecret.server.com'] = {}
    topsecret = config['topsecret.server.com']
    topsecret['Port'] = '50022'     # mutates the parser
    topsecret['ForwardX11'] = 'no'  # same here
    config['DEFAULT']['ForwardX11'] = 'yes'

    with open('example.ini', 'w') as configfile:
        config.write(configfile)



if __name__=='__main__':

    read_original_configurator()