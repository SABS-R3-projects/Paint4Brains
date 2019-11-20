import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import nibabel as nib

root = tk.Tk()

file_x = "80yearold.nii"
xim = nib.load(file_x)
x = xim.get_fdata()
dimension = x.shape

brain = np.array(x[int(dimension[0]/2), :, :])

array = np.ones((40,40))*150
img =  ImageTk.PhotoImage(image=Image.fromarray(brain))

canvas = tk.Canvas(root,width=300,height=300)
canvas.pack()
canvas.create_image(20,20, anchor="nw", image=img)

root.mainloop()


