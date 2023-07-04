import numpy as np

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import ARB, Region, Zone, FlukaRegistry, Transform, Three
from pyg4ometry.fluka.directive import rotoTranslationFromTra2


def Test(vis=False, interactive=False):
    freg = FlukaRegistry()

    # In FLUKA we can choose: either all of the face numbers must
    # refer to vertices in clockwise or anticlockwise direction.  Here
    # we ensure all are clockwise looking out from the centre of the
    # tesselated solid.  This is the right hand corkscrew rule.

    # Rear face:
    vertex1 = Three([0.0, 0.0, 0.0])  # lower left corner
    vertex2 = Three([20.0, 0.0, 0.0])  # lower right corner
    vertex3 = Three([10.0, 20.0, 0.0])  # upper right corner
    vertex4 = Three([0.0, 20.0, 0.0])  # Upper left corner
    face1 = 4321  # clockwise in direction of normal
    # face1 = 1234  # anticlockwise in direction of normal

    # Front face:
    vertex5 = Three([0.0, 0.0, 20.0])  # lower left corner
    vertex6 = Three([20.0, 0.0, 20.0])  # lower right corner
    vertex7 = Three([10.0, 20.0, 20.0])  # upper right corner
    vertex8 = Three([0.0, 20.0, 20.0])  # Upper left corner

    face2 = 5678  # clockwise in direction of normal
    # face2 = 8765 # anticlockwise in direction of normal

    face3 = 2376  # right face
    face4 = 1584  # left face
    face5 = 3487  # top face
    face6 = 1265  # bottom face

    # anticlockwise in direction of noraml
    # face3 = 6732 # right face
    # face4 = 4851 # left face
    # face5 = 7843 # top face
    # face6 = 5621 # bottom face

    vertices = [vertex1, vertex2, vertex3, vertex4, vertex5, vertex6, vertex7, vertex8]
    facenumbers = [face1, face2, face3, face4, face5, face6]

    rtrans = rotoTranslationFromTra2(
        "rppTRF", [[np.pi / 4, np.pi / 4, np.pi / 4], [0, 0, 20]]
    )
    transform = Transform(rotoTranslation=rtrans)

    arb = ARB(
        "ARB_BODY", vertices, facenumbers, transform=transform, flukaregistry=freg
    )

    z = Zone()
    z.addIntersection(arb)

    region = Region("ARB_REG")
    region.addZone(z)
    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {"testStatus": True, "logicalVolume": greg.getWorldVolume(), "vtkViewer": v}


if __name__ == "__main__":
    Test(True, True)
