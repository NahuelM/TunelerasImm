import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import *
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D
import mpl_toolkits.mplot3d.art3d as art3d


def data_for_cylinder_along_z(center_x, center_y, radius, height_z):
    z = np.linspace(0, height_z, 50)
    theta = np.linspace(0, 2*np.pi, 50)
    theta_grid, z_grid=np.meshgrid(theta, z)
    x_grid = radius*np.cos(theta_grid) + center_x
    y_grid = radius*np.sin(theta_grid) + center_y
    return x_grid, y_grid, z_grid

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

Xc, Yc, Zc = data_for_cylinder_along_z(0, 0, 1, 1)
ax.plot_surface(Xc, Yc, Zc, alpha=0.5)

plt.show()