#!/usr/bin/env python

"""
This script loads a GDML files and visualises them in PYGEOMETRY

Options:
--------------------------------------------------------------------------------------------------------------
|path        | --path     | The path to be loaded. Can be a file, comma-separated list of files or a directory|
--------------------------------------------------------------------------------------------------------------
|interactive | -i         | When enabled an interactive IPython session is launched after                     |
|            |            | visualisation window is closed.                                                   |
--------------------------------------------------------------------------------------------------------------
|verbose     | -v         | Print more detailed information                                                   |
--------------------------------------------------------------------------------------------------------------

Example: ./load_gdml.py --path=Par02/Par02FullDetector_geant4parsed.gdml
"""

import os as _os
import ast as _ast
import optparse as _optparse
import pygeometry.gdml as _gdml
import pygeometry.geant4 as _geant4
import pygeometry.vtk as _vtk
try:
    import IPython as _ipython
    _found_ipython = True
except:
    _found_ipython = False

def _appendMeshForView(vis=None):
    registry = _geant4.registry
    worldvol = registry.worldVolume
    meshlist = worldvol.pycsgmesh()

    vis.addPycsgMeshList(meshlist)

    return meshlist

def _loadFiles(path, interactive=False, verbose=False, visualiser=None):
    if isinstance(path, list):
        for fpath in path:
            _loadFiles(fpath, interactive=interactive, verbose=verbose, visualiser=visualiser)

    if _os.path.isdir(str(path)):
        gdmlFiles = [_os.path.abspath(each) for each in _os.listdir(path) if each.endswith('.gdml')]
        for fpath in gdmlFiles:
            _loadFiles(fpath, interactive=interactive, verbose=verbose, visualiser=visualiser)

    elif _os.path.isfile(str(path)):
        if path[-5:] == ".gdml":
            reader   = _gdml.Reader(_os.path.abspath(path))
            _appendMeshForView(vis=visualiser)
        else:
            print "File:", filename
            raise IOError('Missing file or invalid file format, GDML file (.gdml) required')


def load(path, interactive=False, verbose=False):
    vis = _vtk.Viewer()
    _loadFiles(path, interactive, verbose, visualiser=vis)

    vis.view()

    if interactive:
        if _found_ipython:
            _ipython.embed()
        else:
            print "No IPython installed, cannot use interactive mode."

def _tolist_callback(option, opt, value, parser):
  setattr(parser.values, option.dest, [val.strip() for val in value.split(',')])

def _main():
    if __name__ == "__main__":
        usage = ''
        parser = _optparse.OptionParser(usage)
        parser.add_option('-p', '--path', type='string', action='callback', callback=_tolist_callback, default="", help="The path to be loaded. Can be a file, comma-separated list of files or a directory. Valid files must have extension .gdml")
        parser.add_option('-i','--interactive',  action='store_true',default=False, help="Interactive mode (Starts after visualiser is closed)")
        parser.add_option('-v','--verbose',      action='store_true',default=False, help="Print detailed information")

        options,args = parser.parse_args()

        if not options.path:
            print "No target file. Stop."
            parser.print_help()
            return

        if args:
            print "ERROR when parsing, leftover arguments", args
            parser.print_help()
            raise SystemExit

        load(options.path, options.interactive, options.verbose)

    else:
        print "Option parser not availble in interactive mode."


if __name__ == "__main__":
    _main()
