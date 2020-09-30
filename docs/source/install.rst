Install
==========

There are a number of ways to install Paint4Brains on you computer. Which one works best depends on your operative system and whether you intend to further develop the code to fit your needs.

Easy Install (Windows & Ubuntu)
-----------------------------------

Paint4Brains comes with two installer files (one for Windows 10 and one for Ubuntu 18). These will install Paint4Brains as an application on your computer automatically installing all the required dependecies. If you plan to use Paint4Brains as is, we strongly recommend you take this approach because of its simplicity. The latest installers can be found under the assets section of each release.

Developer Install (OSX)
------------------------------

If, however, you want to further develop Paint4Brains to fit you needs or your operative system is not Windows or Ubuntu, you can download the python source code from github. To do this, you first have to clone the github repositry:

.. code-block:: bash

    git clone https://github.com/SABS-R3-projects/Paint4Brains


To run the code you will have to have python3 and pip installed on your computer.

For installation on Linux or OSX, use the following commands. This will create a virtual environment and automatically install all the requirements, as well as create the required metadata

.. code-block:: bash

    ./setup.sh


In order to run the code, activate the previously installed virtual environment, and run the GUI from this environment:

.. code-block:: bash

    ~/(Paint4Brains Locations)$ source env/bin/activate
    ~/(Paint4Brains Locations)$ python Paint4Brains/actualGUI.py

One of the advantages of installing it as source code is that you can now add the brain MRI NIfTI file (.nii, .nii.gz) as a parameter:

.. code-block:: bash

    ~/(Paint4Brains Locations)$ python Paint4Brains/actualGUI.py brain_mri_scan.nii
    
Additionally, you can add both the brain MRI NIfTI file (.nii, .nii.gz) and a NIfTI file containing anatomical labels as parameters. This can be done as follows:

.. code-block:: bash

    ~/(Paint4Brains Locations)$ python Paint4Brains/actualGUI.py brain_mri_scan.nii segmented_brain.nii.gz

