from .. import convert as _convert


def gdml2stl(gdmlFileName, stlFileName="output.gdml", solidName="ws"):
    r = _pyg4.gdml.Reader(gdmlFileName)
    reg = r.getRegistry()
    s = reg.solidDict[solidName]

    _convert.pycsgMeshToStl(s.mesh(), stlFileName)
