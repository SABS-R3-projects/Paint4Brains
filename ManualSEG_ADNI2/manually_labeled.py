import fsl.data.image as ims
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# HAVE TO BE IN THE fslpython ENVIROMENT (COMES WITH FSL)


file_y = "ADNI_002_S_0295_13722_L.nii"
file_z = "ADNI_002_S_0295_13722_R.nii"
file_x = "ADNI_002_S_0295_MR_HarP_135_final_release_2015_Br_20150226095012465_S13408_I474728.nii"

x = ims.Image(file_x)
y = ims.Image(file_y)
z = ims.Image(file_z)


# Doing an animated plot (for fun/to see it)
dimension = x.header["dim"]
fig = plt.figure()
ims = []

dimension = dimension[1:4]
x_data = np.array(x.data)
y_data = -2 * (np.array(y.data) + np.array(z.data)) + 1

print(np.max(x_data[y_data == -1]))

print(np.max(y_data), np.min(y_data))

for i in range(20, dimension[1] - 40):
    im = plt.imshow(np.transpose(x.data[:,i] * y_data[:,i]), animated=True, vmin=-np.max(x_data), vmax=np.max(x_data), origin = "lower", cmap = "Spectral")
    ims.append([im])

ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                repeat_delay=1000)
plt.show()
