import pyg4ometry.pyoce

def convert_mesh_to_poly_Triangulation(m):
    v_and_p = m.toVerticesAndPolygons()

    verts = v_and_p[0]
    triangles = v_and_p[1]

    poly_triangulation = pyg4ometry.pyoce.Poly.Poly_Triangulation(len(verts), len(triangles), False, False)

    for vert, ivert in zip(verts, range(0, len(verts))) :
        p = pyg4ometry.pyoce.gp.gp_Pnt(vert[0], vert[1], vert[2])
        poly_triangulation.SetNode(ivert+1, p)

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

    for shape_name in vis.localmeshes :
        # make oce triangulation
        shape_triangulation = convert_mesh_to_poly_Triangulation(vis.localmeshes[shape_name])

        # Shape builder
        shape = pyg4ometry.pyoce.BRepBuilder.BRepBuilderAPI_MakeShapeOnMesh(shape_triangulation)
        shape.Build()

        # Add shape to assembly
        shape_label = shape_tool.AddShape(shape.Shape(), False, False)

        # Store label for later component creation
        shape_dict[shape_name] = shape_label

    shape_tool.Dump()

    w = pyg4ometry.pyoce.STEPCAFControl.STEPCAFControl_Writer()
    w.Transfer(doc)
    w.WriteFile(stepFileName)


# make a triangulation
if False:
    t = pyg4ometry.pyoce.Poly.Poly_Triangulation(3, 1, False, False)
    p1 = pyg4ometry.pyoce.gp.gp_Pnt(0, 0, 0)
    p2 = pyg4ometry.pyoce.gp.gp_Pnt(5000, 0, 0)
    p3 = pyg4ometry.pyoce.gp.gp_Pnt(0, 5000, 0)
    tri = pyg4ometry.pyoce.Poly.Poly_Triangle(1, 2, 3)
    t.SetNode(1, p1)
    t.SetNode(2, p2)
    t.SetNode(3, p3)
    t.SetTriangle(1,tri)
