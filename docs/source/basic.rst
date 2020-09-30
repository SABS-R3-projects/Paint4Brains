Basic Usage
===========


Getting started
---------------

When you open the Paint4Brains application, a window asking you to "Load brain MRI" will appear. Here you can select the NIfTI file you wish to open in a directory of your system.

Loading an MRI image at the start is required as Paint4Brains will not start without it.

.. image:: _static/screenshots/Load_screen.png
  :width: 500
  :alt: Loading Screen Example
  :align: center

Once a NIfTI file has been selected Paint4Brains will finally open.

.. image:: _static/screenshots/Plain_window.png
  :width: 500
  :alt: Loading Screen Example
  :align: center

On the center of the screen, an image showing the axial slice of the uploaded volume is shown. With both the coronal and sagittal view shown on two side panels on the left.

As you move your mouse around the central image, a yellow cross indicates your position on both of the other view. The view shown in the central image can be changed by double clicking on either of the side images. The 3-D position of your mouse is displayed on the bottom right corner

To explore different slices of the central image, the slider below it can be used. Scrolling the mouse wheel can achieve the same behaviour.

You can zoom in and out any of the images by placing the mouse over the area you wish to enlarge and then scrolling the mouse wheel while pressing the CTRL key. If you are not in Drawing mode this can also be achieved by moving the mouse up or down while holding the right button.

Segmentation
------------

By going to the "Tools" menu bar and clicking on "Segment Brain" the uploaded volume will be segmented. This can also be done by using the CTRL+W shortcut. Once this is clicked you will be asked if you want to run it on a GPU or a CPU. If your computer does not have CUDA installed you should click CPU. However, running it on a GPU will lead to it running a lot faster (around 50 times faster).

Once segmentation has started the following window will appear:

.. image:: _static/screenshots/Plain_window.png
  :width: 500
  :alt: Loading Screen Example
  :align: center

This shows an estimate of how far into the segmentation Paint4Brains is. It also allows you to kill the segmentation at any point. If the segmentation process is killed it will restart from scratch next time you run it.


