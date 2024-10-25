from .. import transformation as _transformation
from .. import pyoce
from ..pyoce.gp import gp_XYZ, gp_Pnt, gp_Dir, gp_Vec, gp_Trsf, gp_Ax1
from ..pyoce.BRepBuilder import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Sewing,
)

import numpy as _np


def convertMeshToPolyTriangulation(m):
    # Take a CSG object mesh and convert to opencascade Poly_triangulation

    # Get verts and polys
    v_and_p = m.toVerticesAndPolygons()

    verts = v_and_p[0]
    triangles = v_and_p[1]

    # create triangulation
    poly_triangulation = pyg4ometry.pyoce.Poly.Poly_Triangulation(
        len(verts), len(triangles), False, False
    )

    # fill vertices
    for vert, ivert in zip(verts, range(len(verts))):
        p = pyg4ometry.pyoce.gp.gp_Pnt(vert[0], vert[1], vert[2])
        poly_triangulation.SetNode(ivert + 1, p)

    # fill triangles
    for tri, itri in zip(triangles, range(len(triangles))):
        tri = pyg4ometry.pyoce.Poly.Poly_Triangle(tri[0] + 1, tri[1] + 1, tri[2] + 1)
        poly_triangulation.SetTriangle(itri + 1, tri)

    return poly_triangulation


def convertMeshToShapeUsingMakeShapeOnMesh(m):
    shape_triangulation = convertMeshToPolyTriangulation(m)
    shape = pyg4ometry.pyoce.BRepBuilder.BRepBuilderAPI_MakeShapeOnMesh(shape_triangulation)
    return shape.Shape()


def convertMeshToShape(m):
    # https://dev.opencascade.org/content/build-topodsshape-triangulation

    # Get verts and polys
    v_and_p = m.toVerticesAndPolygons()

    verts = v_and_p[0]
    triangles = v_and_p[1]

    sewing = BRepBuilderAPI_Sewing(1e-9, True, True, True, False)

    for triangle in triangles:
        v1 = verts[triangle[0]]
        v2 = verts[triangle[1]]
        v3 = verts[triangle[2]]

        p1 = gp_Pnt(v1[0], v1[1], v1[2])
        p2 = gp_Pnt(v2[0], v2[1], v2[2])
        p3 = gp_Pnt(v3[0], v3[1], v3[2])

        polygonBuilder = BRepBuilderAPI_MakePolygon(p1, p2, p3, True)

        # print("--------------------")
        # print(v1[0], v1[1], v1[2])
        # print(v2[0], v2[1], v2[2])
        # print(v3[0], v3[1], v3[2])

        face = BRepBuilderAPI_MakeFace(polygonBuilder.Wire(), True)
        sewing.Add(face.Shape())

    progress = pyg4ometry.pyoce.Message.Message_ProgressRange()
    sewing.Perform(progress)

    return sewing.SewedShape()


def vis2oce(vis, stepFileName="output.step"):
    # create application
    app = pyg4ometry.pyoce.XCAFApp.XCAFApp_Application.GetApplication()

    # create new document
    doc = app.NewDocument(pyg4ometry.pyoce.TCollection.TCollection_ExtendedString("MDTV-CAF"))

    # top label
    top_label = doc.Main()

    # shape tool
    shape_tool = pyg4ometry.pyoce.XCAFDoc.XCAFDoc_DocumentTool.ShapeTool(top_label)

    shape_dict = {}

    iMeshes = 1
    for shape_name in vis.localmeshes:
        # Shape builder
        try:
            shape = convertMeshToShapeUsingMakeShapeOnMesh(vis.localmeshes[shape_name])
            # shape = convertMeshToShape(vis.localmeshes[shape_name])
        except pyg4ometry.pyoce.Standard.Standard_Failure:
            continue

        # Add shape to assembly
        shape_tool.AddShape(shape, False, True)

        # Store label for later component creation
        shape_dict[shape_name] = shape

        # print('vis2oce: iMesh=',iMeshes)

        iMeshes += 1

    iInstance = 1
    for shape_name in vis.localmeshes:
        instances = vis.instancePlacements[shape_name]
        for instance in instances:
            # print('vis2oce: instance=',iInstance, shape_name, instance)
            rotation = instance["transformation"]
            rotation_aa = _transformation.matrix2axisangle(rotation)
            translation = instance["translation"]

            axis = gp_Ax1(
                gp_Pnt(0, 0, 0),
                gp_Dir(rotation_aa[0][0], rotation_aa[0][1], rotation_aa[0][2]),
            )
            trans = gp_Trsf()
            trans.SetValues(
                rotation[0][0],
                rotation[0][1],
                rotation[0][2],
                translation[0],
                rotation[1][0],
                rotation[1][1],
                rotation[1][2],
                translation[1],
                rotation[2][0],
                rotation[2][1],
                rotation[2][2],
                translation[2],
            )

            loc = pyg4ometry.pyoce.TopLoc.TopLoc_Location(trans)

            try:
                shape_located = shape_dict[shape_name].Located(loc, False)
                shape_tool.AddShape(shape_located, False, True)
            except KeyError:
                continue

            iInstance += 1

    shape_tool.UpdateAssemblies()
    # shape_tool.Dump()

    w = pyg4ometry.pyoce.STEPCAFControl.STEPCAFControl_Writer()
    w.Transfer(doc)
    w.WriteFile(stepFileName)
