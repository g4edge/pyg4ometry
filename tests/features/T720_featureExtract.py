import pyg4ometry as _pyg4
import os as _os


def Test(testdata, tmptestdir, vis=False, interactive=False):
    pathToStl = testdata["stl/ST0372507_01_a.stl"]
    cs1 = _pyg4.features.algos.CoordinateSystem([0, 0, 0], [1, 0, 0], [0, 1, 0])
    cs2 = _pyg4.features.algos.CoordinateSystem([0, 0, 20], [1, 0, 0], [0, 1, 0])
    r = _pyg4.features.extract(
        pathToStl,
        planes=[],
        outputFileName=tmptestdir / "T720_featureExtract.dat",
        bViewer=vis,
        bViewerInteractive=interactive,
    )

    return True


if __name__ == "__main__":
    Test()
