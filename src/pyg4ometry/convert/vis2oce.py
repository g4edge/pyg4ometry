import numpy as _np
import pyg4ometry.transformation as _transformation
import pyg4ometry.pyoce
from pyg4ometry.pyoce.gp import gp_XYZ, gp_Pnt, gp_Dir, gp_Vec, gp_Trsf, gp_Ax1

def convert_mesh_to_poly_Triangulation(m):
    # Take a CSG object mesh and convert to opencascade Poly_triangulation

    # Get verts and polys
    v_and_p = m.toVerticesAndPolygons()

    verts = v_and_p[0]
    triangles = v_and_p[1]

    # create triangulation
    poly_triangulation = pyg4ometry.pyoce.Poly.Poly_Triangulation(len(verts), len(triangles), False, False)

    # fill vertices
    for vert, ivert in zip(verts, range(0, len(verts))) :
        p = pyg4ometry.pyoce.gp.gp_Pnt(vert[0], vert[1], vert[2])
        poly_triangulation.SetNode(ivert+1, p)

    # fill triangles
    for tri, itri in zip(triangles, range(0,len(triangles))):
        tri = pyg4ometry.pyoce.Poly.Poly_Triangle(tri[0]+1, tri[1]+1, tri[2]+1)
        poly_triangulation.SetTriangle(itri+1, tri)

    return poly_triangulation

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
    for shape_name in vis.localmeshes :
        # make oce triangulation
        shape_triangulation = convert_mesh_to_poly_Triangulation(vis.localmeshes[shape_name])

        # Shape builder
        shape = pyg4ometry.pyoce.BRepBuilder.BRepBuilderAPI_MakeShapeOnMesh(shape_triangulation)
        shape.Build()

        # Add shape to assembly
        shape_label = shape_tool.AddShape(shape.Shape(), False, True)

        # Store label for later component creation
        shape_dict[shape_name] = shape_label

        print(iMeshes)
        iMeshes += 1

    iInstance = 1
    for shape_name in vis.localmeshes:
        instances = vis.instancePlacements[shape_name]
        for instance in instances:

            print(iInstance, shape_name, instance)
            rotation = instance['transformation']
            rotation_aa = _transformation.matrix2axisangle(rotation)
            translation = instance['translation']

            axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(rotation_aa[0][0], rotation_aa[0][1], rotation_aa[0][2]))
            trans = gp_Trsf()
            trans.SetValues(rotation[0][0], rotation[0][1], rotation[0][2], translation[0],
                            rotation[1][0], rotation[1][1], rotation[1][2], translation[1],
                            rotation[2][0], rotation[2][1], rotation[2][2], translation[2])

            #trans.SetRotation(axis, rotation_aa[1]/_np.pi*180)
            #trans.SetTranslationPart(gp_Vec(translation[0], translation[1], translation[2]))

            #print(rotation_aa)
            #trans.DumpJson()
            #print("")

            loc = pyg4ometry.pyoce.TopLoc.TopLoc_Location(trans)
            comp_label = shape_tool.AddComponent(top_label, shape_dict[shape_name], loc)
            print(comp_label)

            iInstance += 1

    shape_tool.UpdateAssemblies()
    shape_tool.Dump()

    w = pyg4ometry.pyoce.STEPCAFControl.STEPCAFControl_Writer()
    w.Transfer(doc)
    w.WriteFile(stepFileName)
