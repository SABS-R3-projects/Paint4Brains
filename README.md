# **NEVER PULL THIS INTO MASTER**

## This branch is used to easily update the installer

# Paint4Brains: MRI Brain Segmentation Optimized for Elderly Brains for Use in Neurodegenerative Disease

## Motivation
Accurate anatomical segmentation of structure of interest is critical in the neurodegenerative disorder field. Quantitative analysis of medical images is often an important endpoint in research and clinical trials. Atlas-based MRI brain segmentation tools are widely available and used in research settings, however, brains of individuals suffering from Alzheimer’s Disease or Mild Cognitive Impairment are often characterised by localised or widespread atrophy, and pathologies are characterised by enlarged lateral ventricles when compared to a healthy population. Traditional atlas-based MRI segmentation tools have often fallen short in the segmentation of these specific regions, considering they rely on the original segmentation of healthy rather than atrophic brains. The goal of this project is to develop a brain MRI segmentation tool that provides accurate robust segmentation of problematic brain regions across the neurodegenerative spectrum. Furthermore, the methodology should be generalisable to perform well with the typical variance in MRI acquisition parameters and other factors that influence image contrast. The tool should be available and usable by the broad community without constraints due to necessary ancillary software or hardware. Accuracy and computation time should be comparable with commonly available methods.

This open source software was created at the _EPSRC CDT in Sustainable Approached to Biomedical Sciences: Responsible and Reproducible Research - SABS R3_.

## Installation
There are several ways to install the packages. Currently, our team are working on creating installer files for Linux and Windows. The latest version of these are available at [Oxfile](https://oxfile.ox.ac.uk/oxfile/work/extBox?id=83945705F72EA8199D).

Alternatively, to download and run this code as python files, you can clone this repository using git:

```bash
git clone <link to repo>
```

In order to install the required packages, the user will need the presence of Python3 and the [pip3](https://pip.pypa.io/en/stable/) installer. 

For installation on Linux or OSX, use the following commands. This will create a virtual environment and automatically install all the requirements, as well as create the required metadata

```bash
./setup.sh
```

In order to run the code, activate the previously installed virtual environment, and run the GUI from this environment:

```bash
~/(Paint4Brains Locations)$ source env/bin/activate
~/(Paint4Brains Locations)$ python Paint4Brains/actualGUI.py 
```

## Usage
In order to run the GUI, first you need to activate the previously created environment, if you have not done so already. This can be done by typing the following in the home file (the file where you _git pulled_ this repo):

```bash
source env/bin/activate
```

If the environment is created and activated, to run the GUI, please use the following command:

```bash
python Paint4Brains/actualGUI.py
```

The above command can also be run from the GUI folder, but without the _GUI/_ part of the command.

Running the above will automatically open a new window, asking you to load an MRI file. Please do this, as you will not be able to proceed otherwise. After doing this, the GUI will open, displaying a large image of the current location in the brain, 3 smaller images on the left hand side, indicating the 3 possible views:
* Axial
* Coronal
* Saggital

To switch between these views, please click on them individually. The slider bar also allows the user to change the different voxel plane that you are viewing.

There are several menues currently incorporated within the GUI, as follows:
* File
    * New Label
        * Allows the user to open a new labelled file
    * Load Label
        * Allows the user to load a labeled file
    * Save
        * Saves the label currently being editted as .nii file. The second time it is selected it overwrites the previous save
    * Save As
        * Saves the label currently being editted into a new .nii file. Each time it is selected it asks the user for a file name.
* Edit
    * Next Label
        * Allows the user to cycle forward through the labels
    * Previous Label
        * Allows the user to cycle backwards through the labels
    * Select Label
        * Allows the user to manually select a label, by clicking on it, rather than cycling through all labels.
    * Deactivate Drawing
        * Deactivates the edditng tools functionality. This can be reactivated later.
    * Undo (Ctrl+Z)
        * Reverts to previous edit
    * Redo (Ctrl+Shift+Z)
        * Reverts previous undo
* View
    * Recenter View
    * Edditing Toolbar
        * This opens the edditing toolbar, allowing the user to manually edit previously generated segmented maps.
        * The user can choose between a pen and a cross as edditing tools, and a rubber for undo-ing made changes.
        * The user can also cycle between the various generated labels. 
        * **When selecting a label** this label will highlight in red. The user can eddit that label, by using the edditing instruments. When moving on to another label, the changes are saved automatically. **Please do not forget** to also save the final new mask once you have finished edditing. 
        * On the left there is a dropdown box indicating which label is currently selected and allowing the user to select which part of the brain to edit by name.
    * All Labels
        * Clicking on this once, will allow the user to either see one label at a time, and cycle then through all labels
        * Clicking on this a second time will revert the user to seeing all labels at the same time.
* Tools
    * Extract Brain
        * This tool performs brain extraction
    * See Full Brain
        * This tool allows the user to see the full brain again, after extraction
    * Segment Brain
        * This tool takes the provided brain input and runs it through our software's segmentation pipeline.
        * The brain is first conformed using Nilearn and Nibabel.
        * Then, segmentation is performed using QuickNAT (referenced bellow). Depending on the type of hardware used (CPU or GPU), this might take anywhere between 20-30 seconds up to 1 hour. This process, however, is threaded, meaning that the GUI can still be used in the meantime.
        * This process completes by a segmented mask file being generated and saved.
* Help (_currently has no functionality_) 


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause) © [Brennan Abanades Kenyon](https://github.com/brennanaba), [Andrei Roibu](https://github.com/AndreiRoibu), [Pavan Chaggar](https://github.com/PavanChaggar), [Itai Muzhingi](https://github.com/imuzhingi18)

## References
In the creation of this code, material was used from the following papers:

```
@article{roy2019quicknat,
  title={QuickNAT: A fully convolutional network for quick and accurate segmentation of neuroanatomy},
  author={Roy, Abhijit Guha and Conjeti, Sailesh and Navab, Nassir and Wachinger, Christian and Alzheimer's Disease Neuroimaging Initiative and others},
  journal={NeuroImage},
  volume={186},
  pages={713--727},
  year={2019},
  publisher={Elsevier}
}

@article{roy2019bayesian,
  title={Bayesian QuickNAT: Model uncertainty in deep whole-brain segmentation for structure-wise quality control},
  author={Roy, Abhijit Guha and Conjeti, Sailesh and Navab, Nassir and Wachinger, Christian and Alzheimer's Disease Neuroimaging Initiative and others},
  journal={NeuroImage},
  volume={195},
  pages={11--22},
  year={2019},
  publisher={Elsevier}
}
```

## Credits
The team would like to express their gratitude to [Dr Martin Robinson](https://github.com/martinjrobins), the SABS R3 Research Software Engineer, who works closely with us, helping to guide our work and reinforcing the training received during our courses, and [Dr Abhijit Guha Roy](https://github.com/abhi4ssj), the creator of [QuickNAT](https://github.com/ai-med/quickNAT_pytorch), for his help in supporting this project.

This project is being done in collaboration and with support from [GE Healthcare UK](https://www.gehealthcare.co.uk/), with support being provided by [Dr Elisabeth Grecchi](https://www.linkedin.com/in/elisabetta-grecchi) and [Dr Christopher Buckley](https://www.linkedin.com/in/christopher-buckley-24724a13)
 
## Build status
Paint4Brains is currently still in active development. Tests are currently in development. Please check this page regularly for updates. 
