.. _cli:

======================
Command Line Interface
======================

pyg4ometry provides a command line interface that is installed along with the package. Outside
of Python, you will find the executable :code:`pyg4ometry`. This can be executed in a terminal
without the need to start Python.

Any example and test data may be used by prefixing the path with :code:`g4edgetestdata/`, e.g.
:code:`pyg4ometry -i g4edgetestdata/gdml/001_box.gdml -v`. Files are specified from the
`data` directory here: https://github.com/g4edge/testdata/tree/main/data.

The following commands are available: ::

    Usage: pyg4ometry [options]

    Options:
      -h, --help            show this help message and exit
      -a, --analysis        geometry information
      -b, --bounding        calculate bounding box
      -c, --checkoverlaps   check overlaps
      -C CLIP, --clip=CLIP  clip to a box of full widths px,py,pz in mm
      -d COMPAREFILE, --compare=COMPAREFILE
                            comp(a)re geometry
      -e APPENDFILE, --append=APPENDFILE
                            append geometry
      -f FEATUREDATA, --feature=FEATUREDATA
                            feature extraction from simple geometry
                            (planeQuality,circumference)
      -F FEATUREFILE, --featureExtractOutput=FEATUREFILE
                            feature extract output
      -i INFILE, --file=INFILE
                            (i)nput file (gdml, stl, inp, step)
      -I INFO, --info=INFO  information on geometry (tree, reg, instance)
      -l LVNAME, --logical=LVNAME
                            extract logical LVNAME
      -m MATERIAL, --material=MATERIAL
                            material dictionary ("lvname":"nist")
      -n, --nullmesh        disable null mesh exception
      -o OUTFILE, --output=OUTFILE
                            (o)utout file (gdml, inp, usd, vtp)
      -p PLANECUTTER, --planeCutter=PLANECUTTER
                            add (p)plane cutter -p x,y,z,nx,ny,nz
      -P CUTTERFILE, --planeCutterOutput=CUTTERFILE
                            plane cutter output file
      -r TX,TY,TZ, --rotation=TX,TY,TZ
                            rotation (Tait-Bryan) tx,ty,tz (used with
                            append/exchange)
      -s PYTHONSOLID, --solid=PYTHONSOLID
                            solid in python constructor syntax (used with
                            exchange). Registry must be reg and _np used for numpy
      -S SCALE, --gltfScale=SCALE
                            scale factor for gltf conversion
      -t X,Y,Z, --translation=X,Y,Z
                            translation x,y,z (used with append/exchange)
      -v, --view            view geometry
      -V, --verbose         verbose script
      -x LVNAME, --exchange=LVNAME
                            replace solid for logical volume, LVNAME is logical
                            volume name
      -z, --citation        print citation text


Viewing Geometry
----------------
::

  pyg4ometry -i box.gdml -v


Using g4edge test data: ::

  pyg4ometry -i g4edgetestdata/gdml/CompoundExamples/bdsim/vkickers.gdml -v


Converting Geometry
-------------------

Conversion can be done directly by specifying an output format. If this is different
from the input format, it will be converted automatically. ::

  pyg4ometry -i g4edgetestdata/gdml/001_box.gdml -o box.inp


Rotations and Translations
--------------------------

Various commands can be used in combination with a single rotation and translation. In
each case, the rotation is a Tait-Bryan rotation in radians and the translation is in mm.
These are given as three comma-separated numbers with no spaces. Fractions and `pi` can be used.
e.g.: ::

  -r 0,pi/2,0
  -r -3*pi/2,0,0
  -t 10,123.45,100
