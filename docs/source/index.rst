.. Paint4Brains documentation master file, created by
   sphinx-quickstart on Tue Sep 29 11:22:52 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Paint4Brains: Semi-Automated Volumetric Segmentation Tool for Brain MRI Images
==============================================================================

Accurate anatomical segmentation of structure of interest is critical in the neurodegenerative disorder field. Quantitative analysis of medical images is often an important endpoint in research and clinical trials. Atlas-based MRI brain segmentation tools are widely available and used in research settings, however, brains of individuals suffering from Alzheimer’s Disease or Mild Cognitive Impairment are often characterised by localised or widespread atrophy, and pathologies are characterised by enlarged lateral ventricles when compared to a healthy population. Traditional atlas-based MRI segmentation tools have often fallen short in the segmentation of these specific regions, considering they rely on the original segmentation of healthy rather than atrophic brains. The goal of this project is to develop a brain MRI segmentation tool that provides accurate robust segmentation of problematic brain regions across the neurodegenerative spectrum. Furthermore, the methodology should be generalisable to perform well with the typical variance in MRI acquisition parameters and other factors that influence image contrast. The tool should be available and usable by the broad community without constraints due to necessary ancillary software or hardware. Accuracy and computation time should be comparable with commonly available methods.

This open source software was created at the EPSRC CDT in Sustainable Approached to Biomedical Sciences: Responsible and Reproducible Research - SABS R3.


.. toctree::
   install
   basic
   BrainData
