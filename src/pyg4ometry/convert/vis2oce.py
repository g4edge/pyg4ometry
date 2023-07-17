import pyg4ometry.pyoce

def vis2oce(vis):

    # create application
    app = pyg4ometry.pyoce.XCAFApp.XCAFApp_Application.GetApplication()

    # create new document
    doc = app.NewDocument(pyg4ometry.pyoce.TCollection.TCollection_ExtendedString("MDTV-CAF"))

    # top label
    top_label = doc.Main()

    # shape tool
    shape_tool = pyg4ometry.pyoce.XCAFDoc.XCAFDoc_DocumentTool.ShapeTool(top_label)

    return top_label, shape_tool
