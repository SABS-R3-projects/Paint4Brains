import fsl.data.image as ims
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

root = tk.Tk()

file_x = "80yearold.nii"
x = ims.Image(file_x)
dimension = x.header["dim"]

brain = x.data[int(dimension[2]/2), :, :]

array = np.ones((40,40))*150
img =  ImageTk.PhotoImage(image=Image.fromarray(brain))

canvas = tk.Canvas(root,width=300,height=300)
canvas.pack()
canvas.create_image(20,20, anchor="nw", image=img)

root.mainloop()


