=======
pyfluka
=======

View FLUKA geometry meshes and convert to GDML.

==========
Quickstart
==========

Get `pygdml <https://bitbucket.org/jairhul/pygdml>`_.

Clone and install this repository::

  git clone git@bitbucket.org:jairhul/pyfluka.git
  make install

.. code-block:: python

   import pyfluka
   a = pyfluka.Model("pyfluka/tests/test_input/tunnel_cross_section/10.inp")
   a.view_mesh()
   a.write_to_gdml("./my/output/path.gdml")
