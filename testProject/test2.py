from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


def sphere_plot():

    # 球面座標
    R = 1
    theta = np.arange(0, np.pi, 0.01)
    phi = np.arange(0, 2 * np.pi, 0.01)

    # 球面座標を直交座標に変換, outerは外積
    x = R * np.outer(np.cos(phi), np.sin(theta))
    y = R * np.outer(np.sin(phi), np.sin(theta))
    z = R * np.outer(np.ones(np.size(phi)), np.cos(theta))

    fig = plt.figure()
    ax = Axes3D(fig)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.plot_wireframe(x, y, z)
    plt.show()


if __name__ == "__main__":
    sphere_plot()
