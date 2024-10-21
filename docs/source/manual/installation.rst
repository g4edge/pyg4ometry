============
Installation
============

Pre-built wheels
----------------

pyg4ometry runs on all mainstream platforms (Linux, MacOS and Windows) and
requires at least Python 3.7.

The easiest and recommended way to install it is `from PyPI
<https://pypi.org/project/pyg4ometry/>`_: ::

    pip install pyg4ometry

All C++ libraries required by pyg4ometry at runtime are bundled with the Python
wheel.

A Docker image with the latest stable version of pyg4ometry can be downloaded
`from Docker Hub <https://hub.docker.com/repository/docker/g4edge/pyg4ometry>`_

.. code:: console

    $ docker run g4edge/pyg4ometry:latest python
    Python 3.10.12 (main, Jun 11 2023, 05:26:28) [GCC 11.4.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import pyg4ometry
    >>>

Building from source
--------------------

In case you need an unstable version of pyg4ometry or you are interested in
developing, some non-Python dependencies are required.

The following C/C++ libraries (and headers) are required to build the package from source:

* `boost <https://www.boost.org/>`_
* `The GNU Multiple Precision Arithmetic Library (GMP) <https://gmplib.org/>`_
* `The GNU MPFR Library <https://www.mpfr.org/>`_
* `The Computational Geometry Algorithms Library (CGAL) <https://www.cgal.org>`_
* `The Visualisation toolkit (VTK) <https://vtk.org>`_ (including Python bindings)
* `OpenCascade <https://dev.opencascade.org/>`_

Additionally, `CMake <https://cmake.org>`_ is required for building pyg4ometry's C++ extensions.

.. tip::
   Check out the `platform-specific scripts
   <https://github.com/g4edge/pyg4ometry/tree/main/.github/bin>`_ we use to
   obtain dependencies in our CI/CD workflow.

If you want to save yourself the hassle of installing these dependencies, we
recommend building in our Ubuntu Docker image, available `on Docker Hub
<https://hub.docker.com/repository/docker/g4edge/ubuntu>`_:

.. code:: console

   $ docker run -it g4edge/ubuntu:latest
   root@b260417746a1:~#

All Python dependencies will be automatically obtained by pip.

.. note::
   It is worth choosing a Python version for which VTK bindings are available
   (see https://pypi.org/project/vtk/#files). For example, there are limited
   builds for M1 Mac (ARM64).

To install the package, simply run ``pip install`` from the root directory

.. code:: console

   $ git clone https://github.com/g4edge/pyg4ometry
   $ cd pyg4ometry
   $ pip install .

.. tip::
   The building uses CMake through `scikit-build-core
   <https://scikit-build-core.readthedocs.io>`_. Build errors or warnings are
   typically from cmake and can help determining the missing dependency.

.. note::
   If you are building for windows you are going to need Visual Studio and
   the appropriate command line tools.

.. warning::
   the package is built in parallel by default and is memory intensive! Make
   sure you have enough computational resources. If not, consult the
   scikit-build-core documentation to learn how to reduce the number of
   threads.
