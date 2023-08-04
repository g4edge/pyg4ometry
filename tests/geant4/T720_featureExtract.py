import pyg4ometry as _pyg4
import os as _os


def Test(vis=False, interactive=False):
    pathToStl = _os.path.dirname(_pyg4.__file__) + "/../../test/stl/ST0372507_01_a.stl"
    cs1 = _pyg4.features.algos.CoordinateSystem([0, 0, 0], [1, 0, 0], [0, 1, 0])
    cs2 = _pyg4.features.algos.CoordinateSystem([0, 0, 20], [1, 0, 0], [0, 1, 0])
    r = _pyg4.features.extract(
        pathToStl,
        planes=[],
        outputFileName=_os.path.join(_os.path.dirname(__file__), "T720_featureExtract.dat"),
        bViewer=vis,
        bViewerInteractive=interactive,
    )

    return True


if __name__ == "__main__":
    Test()
