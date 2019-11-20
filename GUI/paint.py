from tkinter import *
from tkinter import ttk, colorchooser, filedialog
import nibabel as nib
import numpy as np
from PIL import Image, ImageTk


file_x = "80yearold.nii"
xim = nib.load(file_x)
x = xim.get_fdata()
dimension = x.shape

brain = np.array(x[int(dimension[0]/2), :, :])



class main:
    def __init__(self, master):
        self.master = master
        self.color_fg = 'black'
        #sets background color
        self.color_bg = 'white'
        self.old_x = None
        self.old_y = None
        self.penwidth = 5
        self.drawWidgets()
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    def paint(self, e):
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, e.x, e.y, width=self.penwidth, fill=self.color_fg,
                               capstyle=ROUND, smooth=True)

        self.old_x = e.x
        self.old_y = e.y

    def reset(self, e):
        self.old_x = None
        self.old_y = None

    def changeW(self, e):
        self.penwidth = e

    #Someone fix me!!!!!
    def save(self):
        file = filedialog.asksaveasfilename(filetypes=[('Portable Network Graphics', '*.png')])
        if file:
                print("NOT SAVING THIS SHIT!!!")

    def clear(self):
        self.c.delete(ALL)

    def change_fg(self):
        self.color_fg = colorchooser.askcolor(color=self.color_fg)[1]

    def change_bg(self):
        self.color_bg = colorchooser.askcolor(color=self.color_bg)[1]
        self.c['bg'] = self.color_bg

    def drawWidgets(self):
        self.controls = Frame(self.master, padx=5, pady=5)
        Label(self.controls, text='Pen Width: ', font=('', 15)).grid(row=0, column=0)
        self.slider = ttk.Scale(self.controls, from_=5, to=100, command=self.changeW, orient=HORIZONTAL)
        self.slider.set(self.penwidth)
        self.slider.grid(row=0, column=1, ipadx=30)
        self.controls.pack()

        self.c = Canvas(self.master, width=500, height=400, )
        self.c.pack(fill=BOTH, expand=True)
        img = ImageTk.PhotoImage(image=Image.fromarray(brain))
        self.c.create_image(20, 20, anchor="nw", image=img)

        menu = Menu(self.master)
        self.master.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label='File..', menu=filemenu)
        filemenu.add_command(label='Export..', command=self.save)
        colormenu = Menu(menu)
        menu.add_cascade(label='Colors', menu=colormenu)
        colormenu.add_command(label='Brush Color', command=self.change_fg)
        colormenu.add_command(label='Background Color', command=self.change_bg)
        optionmenu = Menu(menu)
        menu.add_cascade(label='Options', menu=optionmenu)
        optionmenu.add_command(label='Clear Canvas', command=self.clear)
        optionmenu.add_command(label='Exit', command=self.master.destroy)


if __name__ == '__main__':


    root = Tk()
    main(root)
    root.title('DrawingApp')
    root.mainloop()