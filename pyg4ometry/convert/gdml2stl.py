import pyg4ometry as _pyg4

def gdml2stl(gdmlFileName, stlFileName = "output.gdml", solidName = "ws") :
    r = _pyg4.gdml.Reader(gdmlFileName)
    reg = r.getRegistry()
    s = reg.solidDict[solidName]

    _pyg4.convert.pycsgMeshToStl(s.mesh(),stlFileName)



