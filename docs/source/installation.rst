============
Installation
============


Requirements
------------

pyg4ometry is developed exclusively for Python 3 (Python2 is deprecated). It is developed on Python 3.9 and 3.10.


 * `VTK (Visualisation toolkit) <https://vtk.org>`_ (including Python bindings)
 * `antlr4 <https://www.antlr.org>`_
 * `cython <https://cython.org>`_
 * `CGAL <https://www.cgal.org>`_
 * pybind11

Packages that are required but will be found through PIP automatically:

 * `matplotlib <https://matplotlib.org>`_
 * `GitPython <https://gitpython.readthedocs.io/en/stable/>`_
 * pandas
 * pypandoc
 * networkx
 * numpy
 * sympy

**Optional**

 * `Freecad  <https://www.freecadweb.org>`_ for CAD conversion.

.. note:: A full list can be found in :code:`pyg4ometry/setup.py`.

.. note:: if you are choosing a python version, it is worth choosing according to which
	  version VTK provides a python build of through PIP if you use that. See
	  https://pypi.org/project/vtk/#files  For example, there are limited builds
	  for M1 Mac (ARM64).


Installation
------------

To install pyg4ometry, simply run ``make install`` from the root pyg4ometry
directory::

  cd /my/path/to/repositories/
  git clone http://bitbucket.org/jairhul/pyg4ometry
  git checkout develop
  cd pyg4ometry

  make install

.. note::
   To build using the git directory and not installing into /usr/local use ``make develop``
   instead of ``make install``

To build pycsg with cpython::

  make build_ext

Or install from pypi::

  pip install pyg4ometry

or alternatively, run ``make develop`` from the same directory to ensure
that any local changes are picked up.

Docker image
------------

#. Download and install `Docker desktop <https://www.docker.com/products/docker-desktop>`_
#. open a terminal (linux) or cmd (windows)
#. (windows) Start `Xming <https://sourceforge.net/projects/xming/>`_ or `Vxsrv <https://sourceforge.net/projects/vcxsrv/>`_
#. Download the `pyg4ometry docker file <https://bitbucket.org/jairhul/pyg4ometry/raw/82373218033874607f682a77be33e03d5b6706aa/docker/Dockerfile-ubuntu-pyg4ometry>`_
#. ``docker build -t ubuntu-pyg4ometry -f Dockerfile-ubuntu-pyg4ometry .``

If you need to update increment the variable ``ARG PYG4OMETRY_VER=1``

To start the container

#. open a terminal (linux/mac) or cmd (windows)
#. get your IP address ``ifconfig`` (linux/mac) or ``ipconfig /all`` (windows)
#. Start XQuartz (mac) or Xming/Vxsrv (windows). For Xming/Vxsrv (might need to play with the settings when launching)
#. ``docker run -ti -v /tmp/.X11-unix:/tmp/.X11-unix -v YOURWORKDIR:/tmp/Physics -e DISPLAY=YOUR_IP ubuntu-pyg4ometry`` (the ``-v /tmp/.X11-unix:/tmp/.X11-unix`` is only required for mac/linux)

Test the installation

#. ``docker> cd pyg4ometry/pyg4ometry/test/pythonGeant4/``
#. ``docker> ipython``
#. ``python> import pyg4ometry``
#. ``python> import T001_Box``
#. ``python> T001_Box.Test(True,True)``

Linux installation
------------------

There are docker files for Centos 7 and Ubuntu 20. The docker files can be used as list of instructions for
installation for each of these OSes.

* `Ubuntu 20.02 <https://bitbucket.org/jairhul/pyg4ometry/raw/82373218033874607f682a77be33e03d5b6706aa/docker/Dockerfile-ubuntu-pyg4ometry>`_
* `Centos 7 <https://bitbucket.org/jairhul/pyg4ometry/raw/befcd36c1213670830b854d02c671ef14b3f0f5c/docker/Dockerfile-centos-pyg4ometry>`_


FreeCAD support for CAD to GDML conversion
------------------------------------------

For FreeCAD support and you already have it installed you  need to add library to PYTHONPATH, for example

.. code-block :: console

   export PYTHONPATH=/opt/local/libexec/freecad/lib/

Building FreeCAD can be a pain for MAC so

.. code-block :: console

   mkdir FreeCAD
   cd FreeCAD
   set FCROOT=$pwd
   wget  https://github.com/FreeCAD/FreeCAD/archive/0.19_pre.tar.gz
   tar zxf 0.19_pre.tar.gz
   mkdir build
   mkdir install
   cd build
   cmake ../FreeCAD-0.18.4 -DCMAKE_INSTALL_PREFIX=../install \
   -DCOIN3D_LIBRARIES=/opt/local/Library/Frameworks/Inventor.framework/Libraries/libCoin.dylib -DBUILD_FEM=0 \
   -DBUILD_MATERIAL=0 -DBUILD_SHIP=0 -DBUILD_DRAFT=0 -DBUILD_TUX=0 -DBUILD_ARCH=0 -DBUILD_PLOT=0 \
   -DBUILD_OPENSCAD=0
   make -jN
   make install
   export PYTHONPATH=$PYTHONPATH:$FCROOT/install



Python 3.9
----------

At the time of writing, there are limited VTK distributions for Python 3.9 on pypi (what
PIP uses when finding packages). However,
you can have VTK with Python 3.9 through say MacPorts or by compiling it yourself. In this
case, you can comment out the VTK requirement from the setup.py around line 86, as long
as you know you can :code:`import vtk` ok in your Python installation.

.. warning:: ANTLR will create an unbelievable amount of warnings when using a different
	     ANRLR version that the one the parser was generated with. It should work
	     though. We are trying to include multiple versions of the ANTLR parser
	     to avoid this in future.
