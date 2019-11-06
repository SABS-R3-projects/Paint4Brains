import fsl.data.image as ims
from fsl.wrappers.bet import bet
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# HAVE TO BE IN THE fslpython ENVIROMENT (COMES WITH FSL)

file_x = "80yearold.nii"
file_y = "80yearold_bet.nii.gz"

x = ims.Image(file_x)
# Bet takes an image and extracts it to a file
bet(x, file_y, "R")
y = ims.Image(file_y)

# Showing how images work and different parameters yoi can call
print(x)
print(x.dtype)
print(x.data)
print("\nFirst line\n")
print(x.data[100][110])
print("\n")
# Header is a dictionary so you can call all the info
print(x.header)

# Doing an animated plot (for fun/to see it)
dimention = x.header["dim"]
fig = plt.figure()
ims = []
for i in range(dimention[3]):
    im = plt.imshow(y.data[:, :, i], animated=True)
    ims.append([im])

ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                repeat_delay=1000)
plt.show()
