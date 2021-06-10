import numpy as np
from stl import mesh, Mesh
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import math
import streamlit as st


def get_cycles(xs, ys):
    _xs, _ys = [xs[0]], [ys[0]]
    for i in range(1, len(xs)):
        if not (xs[i] == xs[i - 1] and ys[i] == ys[i - 1]):
            _xs.append(xs[i])
            _ys.append(ys[i])
    xs, ys = _xs, _ys
    past_coordinates = [(xs[0], ys[0])]
    shapes = []
    i = 1
    while i < len(xs):
        coor_i = (xs[i], ys[i])
        if coor_i not in past_coordinates:
            past_coordinates.append(coor_i)
        else:
            past_coordinates.append(coor_i)
            past_coordinates = past_coordinates[past_coordinates.index(coor_i):]
            if len(past_coordinates) > 3:
                shapes.append(past_coordinates[past_coordinates.index(coor_i):])
            if i + 1 < len(xs): past_coordinates = [(xs[i + 1], ys[i + 1])]
            i += 1
        i += 1
    return shapes


def plot_mesh(M: Mesh):

    if st.sidebar.checkbox("Rotate mesh (90) along [-1, 0, 0]", True):
        M.rotate([-1, 0, 0], math.radians(90))

    # Rotate Anti Clockwise along + x-axis
    # M.rotate([1, 0, 0], math.radians(90))
    # Rotate Anti Clockwise along + y-axis
    # M.rotate([0, 1, 0], math.radians(90))
    # Rotate Anti Clockwise along + z-axis
    # M.rotate([0, 0, 1], math.radians(90))

    fig = plt.figure()
    axes = mplot3d.Axes3D(fig)
    axes.add_collection3d(mplot3d.art3d.Poly3DCollection(M.vectors))
    scale = M.points.flatten()
    axes.auto_scale_xyz(scale, scale, scale)
    plt.xlabel("x-axis")
    plt.ylabel("y-axis")
    st.pyplot(fig)


def correct_z_height(z_height: float, zs_heights: list):
    idx = np.searchsorted(zs_heights, z_height)
    if abs(z_height - zs_heights[idx - 1]) < abs(zs_heights[idx] - z_height):
        z_height = zs_heights[idx - 1]
    else:
        z_height = zs_heights[idx]
    return z_height


def main(M: Mesh):

    st.write("# Mesh Plot")
    plot_mesh(M)

    option = st.sidebar.radio("How you want to perform scanning", [
        "From -z to +z",
        "From +z to -z",
        "From +x to -x",
        "From -x to +x",
        "From +y to -y",
        "From -y to +y",
    ])

    if option == "From -z to +z":
        pass
    elif option == "From +z to -z":
        # Rotate 180 degree along x-axis
        M.rotate([1, 0, 0], math.radians(180))
    elif option == "From +x to -x":
        # Rotate 90 degree clockwise along + y-axis
        M.rotate([0, -1, 0], math.radians(90))
    elif option == "From -x to +x":
        # Rotate 90 degree clockwise along - y-axis
        M.rotate([0, 1, 0], math.radians(90))
    elif option == "From +y to -y":
        # Rotate 90 degree clockwise along - x-axis
        M.rotate([1, 0, 0], math.radians(90))
    elif option == "From -z to +z":
        # Rotate 90 degree clockwise along + x-axis
        M.rotate([-1, 0, 0], math.radians(90))

    zs = sorted([(z, (idx_i, idx_j)) for idx_i, _zs in enumerate(M.z) for idx_j, z in enumerate(_zs)])

    d = {}
    for z, idx in zs:
        z = z
        if z in d:
            d[z].append(idx)
        else:
            d[z] = [idx]

    zs_heights = list(d.keys())

    st.write("---")

    st.write("# Plots for all z-heights")

    new_zs_heights = []
    for z_height in zs_heights:

        indices = np.array(d[z_height])
        xs = [x for x in M.x[indices[:, 0], indices[:, 1]]]
        ys = [y for y in M.y[indices[:, 0], indices[:, 1]]]

        # if len(xs) < 4: continue
        if len(np.unique(xs)) < 2: continue
        if len(np.unique(ys)) < 2: continue

        new_zs_heights.append(z_height)

        fig = plt.figure()
        plt.scatter(xs, ys, c='y')
        plt.plot(xs, ys, c='b')
        plt.title(f"z_height: {z_height}")
        st.pyplot(fig)

    st.write("---")

    z_height = st.sidebar.number_input("Enter z-height to get sub cycles",
                                       min_value=float(min(new_zs_heights)),
                                       max_value=float(max(new_zs_heights)),
                                       value=float(new_zs_heights[-1]),
                                       step=float(np.mean(new_zs_heights)))

    st.write(f"# All sub-cycles for z-height: {z_height}")

    z_height = correct_z_height(z_height, new_zs_heights)
    indices = np.array(d[z_height])
    xs = np.array([x for x in M.x[indices[:, 0], indices[:, 1]]])
    ys = np.array([y for y in M.y[indices[:, 0], indices[:, 1]]])

    shapes = get_cycles(xs, ys)

    for idx, shape in enumerate(shapes):
        shape = np.array(shape)
        xs = shape[:, 0]
        ys = shape[:, 1]
        fig = plt.figure()
        plt.scatter(xs, ys, c='y')
        plt.plot(xs, ys, c='b')
        plt.title(f"Sub shape({idx + 1}) for z-height: {z_height}")
        st.pyplot(fig)


fh = st.file_uploader("Upload file", ['stl'])
if fh is not None:
    M: Mesh = mesh.Mesh.from_file("stl", fh=fh)
else:
    M: Mesh = mesh.Mesh.from_file("default.stl")
main(M)
