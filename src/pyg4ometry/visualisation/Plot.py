import matplotlib.pyplot as _plt

from .Convert import vtkPolyDataToNumpy as _vtkPolyDataToNumpy


def AddCutterDataToPlot(
    filename, projection="zx", ax=None, unitsFactor=1.0, colour="k", linewidth=0.5, alpha=1.0
):
    """
    Add cutter data to a plot or draw in a new figure if no axis object given.

    :param filename: file name of exported cutter data from visualiser.
    :type filename: str
    :param projection: which two axes to plot in a 2D plot from the 3D data. e.g. zx, zy.
    :type projection: str
    :param ax: matplotlib axes instance.
    :type ax: matplotlib.axes._axes.Axes
    :param unitsFactor: numerical scaling factor for coordinates (e.g. 0.001 for plotting in meters).
    :type unitsFactor: float
    :param colour: matplotlib.pyplot.plot colour argument
    :type colour: str
    :param linewidth: matplotlib.pyplot.plot linewidth argument
    :type linewidth: float
    :param alpha: matplotlib.pyplot.plot alpha argument for transparency
    :type alpha: float

    If used without an axes, a new figure and axes will be created.

    The project specifies the order of plotting, so 'zx' would give z in the plot's x axis
    and 'x' in plot's y axis. Any combination of 'x', 'y' and 'z' are accepted and must be
    different. e.g. any of 'xy', 'xz', 'yx', 'yz', 'zx', 'zy'.
    """
    reapplyLims = False
    if not ax:
        f = _plt.figure()
        ax = f.add_subplot(111)
    else:
        reapplyLims = True
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

    if len(projection) != 2:
        msg = "projection must be 2 letters including x, y, z"
        raise ValueError(msg)

    dims = ["x", "y", "z"]
    ind1 = dims.index(projection[0])
    ind2 = dims.index(projection[1])
    if ind1 == ind2:
        msg = "projection must contain 2 unique letters"
        raise ValueError(msg)

    polyData = _vtkPolyDataToNumpy(filename)
    for poly in polyData:
        ax.plot(
            poly[:, ind1] * unitsFactor,
            poly[:, ind2] * unitsFactor,
            c=colour,
            lw=linewidth,
            alpha=alpha,
        )

    if reapplyLims:
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
