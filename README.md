[![Build Status](https://travis-ci.com/SABS-R3-projects/Paint4Brains.svg?branch=master)](https://travis-ci.com/SABS-R3-projects/Paint4Brains)
[![Documentation Status](https://readthedocs.org/projects/paint4brains/badge/?version=latest)](https://paint4brains.readthedocs.io/en/latest/?badge=latest)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/SABS-R3-projects/Paint4Brains.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/SABS-R3-projects/Paint4Brains/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/SABS-R3-projects/Paint4Brains.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/SABS-R3-projects/Paint4Brains/alerts/)
[![GitHub All Releases](https://img.shields.io/github/downloads/SABS-R3-projects/Paint4Brains/total?color=green)](https://github.com/SABS-R3-projects/Paint4Brains/releases)
[![GitHub](https://img.shields.io/github/license/SABS-R3-projects/Paint4Brains)](https://github.com/SABS-R3-projects/Paint4Brains/blob/master/LICENSE)

# Paint4Brains: MRI Brain Segmentation Optimized for Elderly Brains for Use in Neurodegenerative Disease

## Motivation
Accurate anatomical segmentation of structure of interest is critical in the neurodegenerative disorder field. Quantitative analysis of medical images is often an important endpoint in research and clinical trials. Atlas-based MRI brain segmentation tools are widely available and used in research settings, however, brains of individuals suffering from Alzheimer’s Disease or Mild Cognitive Impairment are often characterised by localised or widespread atrophy, and pathologies are characterised by enlarged lateral ventricles when compared to a healthy population. Traditional atlas-based MRI segmentation tools have often fallen short in the segmentation of these specific regions, considering they rely on the original segmentation of healthy rather than atrophic brains. The goal of this project is to develop a brain MRI segmentation tool that provides accurate robust segmentation of problematic brain regions across the neurodegenerative spectrum. Furthermore, the methodology should be generalisable to perform well with the typical variance in MRI acquisition parameters and other factors that influence image contrast. The tool should be available and usable by the broad community without constraints due to necessary ancillary software or hardware. Accuracy and computation time should be comparable with commonly available methods.

This open source software was created at the _EPSRC CDT in Sustainable Approached to Biomedical Sciences: Responsible and Reproducible Research - SABS R3_.

## Installation
There are several ways to install the packages. There are installer files for Linux and Windows, the latest versions of these are available as [releases](https://github.com/SABS-R3-projects/Paint4Brains/releases).

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

For a more detailed description [read the docs](https://paint4brains.readthedocs.io/en/latest/index.html).

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
