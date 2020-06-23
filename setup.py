from setuptools import setup, find_packages

setup(
    name='Paint4Brains',
    version='0.0.1',
    description='MRI Brain Segmentation Optimized for Elderly Brains for Use in Neurodegenerative Disease',
    license='BSD 3-clause license',
    maintainer='Brennan Abanades, Pavanjit Chaggar, Itai Muzhingi, Andrei-Claudiu Roibu',
    maintainer_email='brennan.abanadeskenyon@stx.ox.ac.uk; pavanjit.chaggar@exeter.ox.ac.uk; itai.muzhingi@balliol.ox.ac.uk; andrei-claudiu.roibu@dtc.ox.ac.uk',
    include_package_data=True,
    packages = find_packages(include=('Paint4Brains', 'Paint4Brains.*', 'Paint4Brains.GUI.*')),
    install_requires=[
        'pip>=20.0.2',
        'certifi>=2019.9.11',
        'cycler>=0.10.0',
        'kiwisolver>=1.1.0',
        'matplotlib>=3.1.1',
        'nibabel>=2.5.1',
        'numpy>=1.17.3',
        'pandas>=0.25.3',
        'patsy>=0.5.1',
        'PyOpenGL>=3.1.0',
        'pyparsing>=2.4.5',
        'PyQt5==5.13.2',
        'PyQt5-sip>=12.7.0',
        'pyqtgraph>=0.10.0',
        'python-dateutil>=2.8.1',
        'pytz>=2019.3',
        'scipy>=1.3.1',
        'seaborn>=0.9.0',
        'six>=1.13.0',
        'statsmodels>=0.10.1',
        'tornado>=6.0.3',
        'tensorflow==1.15.2',
        'torch==1.2.0',
        'torchvision==0.4.0',
        'h5py>=2.8.0',
        'tensorboardX>=1.2',
        'configparser',
        'nilearn==0.5.2',
	'sklearn',
        'nn_common_modules @ https://github.com/shayansiddiqui/nn-common-modules/releases/download/v1.0/nn_common_modules-1.0-py2.py3-none-any.whl',
        'squeeze_and_excitation @ https://github.com/abhi4ssj/squeeze_and_excitation/releases/download/v1.0/squeeze_and_excitation-1.0-py2.py3-none-any.whl',
        ],
)
