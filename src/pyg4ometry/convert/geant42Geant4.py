import vtk as _vtk
from ..visualisation import Convert as _Convert
from ..geant4 import solid as _solid


def geant4Solid2Geant4Tessellated(solid):
    pycsg_mesh = solid.mesh()

    # Use VTK to reduce all polygons to triangles
    # as CSG operations can produce arbitrary polygons
    # which cannot be used in Tessellated Solid
    meshVTKPD = _Convert.pycsgMeshToVtkPolyData(pycsg_mesh)
    vtkFLT = _vtk.vtkTriangleFilter()
    vtkFLT.AddInputData(meshVTKPD)
    vtkFLT.Update()
    triangular = vtkFLT.GetOutput()

    meshTriangular = []
    for i in range(triangular.GetNumberOfCells()):
        pts = triangular.GetCell(i).GetPoints()
        vertices = [pts.GetPoint(i) for i in range(pts.GetNumberOfPoints())]
        # The last 3-tuple is a dummy normal to make it look like STL data
        meshTriangular.append((vertices, (None, None, None)))

    name = solid.name + "_asTesselated"
    reg = solid.registry
    mesh_type = _solid.TessellatedSolid.MeshType.Stl
    tesselated_solid = _solid.TessellatedSolid(name, meshTriangular, reg, meshtype=mesh_type)

    return tesselated_solid


def geant4Solid2Geant4Tessellated_NoVTK(solid):
    pycsg_mesh = solid.mesh()

    meshTriangular = []

    vAndP = pycsg_mesh.toVerticesAndPolygons()

    for t in vAndP[1]:
        vert = [vAndP[0][idx] for idx in t]
        vert = [vert, (None, None, None)]
        # print(vert)
        meshTriangular.append(vert)

    name = solid.name + "_asTesselated"
    reg = solid.registry
    mesh_type = _solid.TessellatedSolid.MeshType.Stl
    tesselated_solid = _solid.TessellatedSolid(name, meshTriangular, reg, meshtype=mesh_type)

    return tesselated_solid
