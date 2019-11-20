import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

file_x = "80yearold.nii"

xim = nib.load(file_x)
x = xim.get_fdata()
dimension = x.shape



# Showing how images work and different parameters you can call
print(x)
print(x.dtype)
print("\n")
# Header is a dictionary so you can call all the info


# Doing an animated plot (for fun/to see it)

fig = plt.figure()
ims = []
# Doing animation along the 3rd dimension. Therefore dimension[3] and data[:,:,i]
for i in range(dimension[2]):
    im = plt.imshow(x[:, :, i], animated=True)
    ims.append([im])

ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                repeat_delay=1000)
plt.show()
