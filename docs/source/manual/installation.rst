============
Installation
============

Installing from PyPi
--------------------

The easiest way to install pyg4ometry is to install from PyPi. Pyg4ometry
has many external requirements which need to be provided by a package
manager on your system. To install using PyPi::

    pip install pyg4ometry

If installing for MacOS you will need to install (opencascade, cgal, gmp, mpfr, boost, vtk)::

    brew install opencascade cgal gmp mpfr boost vtk

If installing for Windows you will need to install (opencascade, cgal)::

    conda install occt cgal-cpp

Building from source
--------------------

Requirements
^^^^^^^^^^^^

pyg4ometry is developed exclusively for Python 3 (Python2 is deprecated). It is developed on Python 3.9 and 3.10.

 * `VTK (Visualisation toolkit) <https://vtk.org>`_ (including Python bindings)
 * `antlr4 <https://www.antlr.org>`_
 * `cython <https://cython.org>`_
 * `CGAL <https://www.cgal.org>`_
 * pybind11
 * cmake

Packages that are required but will be found through PIP automatically:

 * `matplotlib <https://matplotlib.org>`_
 * `GitPython <https://gitpython.readthedocs.io/en/stable/>`_
 * pandas
 * pypandoc
 * networkx
 * numpy
 * sympy

.. note:: A full list can be found in :code:`pyg4ometry/pyproject.toml`.

.. note:: if you are choosing a python version, it is worth choosing according to which
	  version VTK provides a python build of through PIP if you use that. See
	  https://pypi.org/project/vtk/#files  For example, there are limited builds
	  for M1 Mac (ARM64).


Building
^^^^^^^^

To install pyg4ometry, simply run ``make install`` from the root pyg4ometry
directory::

    cd /my/path/to/repositories/
    git clone https://github.com/g4edge/pyg4ometry
    cd pyg4ometry

    pip install .

If you wish to develop an extension or modify pyg4ometry then run::

    pip install -e .

as this will not install pyg4ometry, but the git repository directory will
be used for the package. To confirm the install location run::

    pip list | grep pyg4ometry

.. note::
    The building uses skikit-build which required cmake. Build errors
    or warnings are typically from cmake and can help determining the
    missing dependency

.. note::
    If you are building for windows you are going to need Visual Studio and
    the appropriate command line tools

Docker image (needs updating)
-----------------------------

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

Developer notes
---------------

Building the manual
^^^^^^^^^^^^^^^^^^^

To build the documentation ::

    pip install '.[docs]' # to install docs building dependencies
    cd pyg4ometry/docs
    make
    <your browser> build/html/index.html` # to view the docs

Running tests
^^^^^^^^^^^^^

Running tests ::

    pip install '.[test]' # to install test running dependencies
    pytest


Git
^^^

pre-commit::

    pre-commit install  # to setup pre-commit in source dir (only once)
    pre-commit run --all-files # run pre-commit locally
    pre-commit run --all-files black  #run only black

Start commit message with the submodule or area changes::

    submodule : (type of change) detailed notes

for example::

    pycgal : (extra functionality) more 2d mesh processing

Pull requests. PR messages should just explain the change in a concise way as they will form part of the change log
e.g::

    FLUKA region viewer
