.. _viewing:

================
Viewing Geometry
================

pyg4ometry uses the Visualisation Toolkit - VTK - to view geometry. This provides a window with a
3D view of a model that can be manipulated with a cursor (rotate, pan, zoom, click). Most manipulation
can be done by calling methods on the instance of the visualiser class in the terminal.

Basic loading and viewing is described in :ref:`loading`. Here, more detailed individual features are
described.

Visualiser Classes
------------------

Several visualiser classes are provided but ultimately, the only difference is the default colouring
of volumes.

* :code:`VtkViewer` - all in grey
* :code:`VtkViewerColoured` - user-provided dictionary of materials to colours
* :code:`VtkViewerColouredMaterial` - default dictionary of material colours included

Both :code:`VtkViewerColoured` and :code:`VtkViewerColouredMaterial` inherit :code:`VtkViewer`
and have the same functionality and differ only in colouring of volumes.

Generally:

.. code-block:: python

    v = pyg4ometry.visualisation.VtkViewer()
    v.addLogicalVolume(lv)
    v.view()  # or
    v.view(interactive=False)  # to not block the terminal


Exact documentation can be found in :ref:`module-docs-visualisation`.

If not adding a whole geometry tree, then individual solids can be added and overlaid
with transparency for comparison purposes.

Using the Visualiser
--------------------

+-----------------------------+--------------------------------------------------+
| **Action**                  | **Outcome**                                      |
+=============================+==================================================+
| click and drag              | rotate the geometry                              |
+-----------------------------+--------------------------------------------------+
| shift key + click and drag  | pan (move) the geometry                          |
+-----------------------------+--------------------------------------------------+
| right click                 | 'pick' a volume and print out its name if found  |
+-----------------------------+--------------------------------------------------+
| scroll                      | zoom in and out                                  |
+-----------------------------+--------------------------------------------------+

Rotating
********

.. figure:: http://www.pp.rhul.ac.uk/bdsim/pyg4ometry-uploads/pan-rotate-v1.gif
   :width: 80%
   :align: center

Rotate by clicking and dragging, then release.


Zooming
*******

.. figure:: http://www.pp.rhul.ac.uk/bdsim/pyg4ometry-uploads/zooming-v1.gif
   :width: 80%
   :align: center

Scroll in and out on a mouse or trackpad whilst pointing at the visualiser.


Panning And Rotating
********************

.. figure:: http://www.pp.rhul.ac.uk/bdsim/pyg4ometry-uploads/pan-rotate-v1.gif
   :width: 80%
   :align: center

Click and drag to rotate. Hold the shift key on the keyboard, then click
and drag to pan.

When we rotate the geometry it may twist in multiple angles. To rotate in a specific
way we can click and drag and draw it small circles where the geometry will precess.

.. figure:: http://www.pp.rhul.ac.uk/bdsim/pyg4ometry-uploads/precessing-v1.gif
   :width: 80%
   :align: center


Picking
*******

If you right click on a volume and look at the terminal, if pyg4ometry can find
a volume behind the point clicked it will print out the name.

.. figure:: http://www.pp.rhul.ac.uk/bdsim/pyg4ometry-uploads/picking-v1.gif
   :width: 80%
   :align: center


Solid or Wireframe
------------------

When using the visualiser window, the same geometry can be viewed as solid surfaces or
as a wireframe by pressing :code:`s` key or the :code:`w` key respectively.

Note, the original visualisation has the outermost volume as wireframe and the contents
as solid. Once, the wireframe or solid option has been chosen, all volumes will have the
same style.

Logical Volume
--------------

A :code:`pyg4ometry.geant4.LogicalVolume` instance can be added to the visualiser. A
logical volume has no concept of translation or rotation on its own, so it is placed
in the centre of the visualiser coordinate system, i.e. in its own frame.

.. code-block:: python

    lv  # pyg4ometry.geant4.LogicalVolume instance
    v = pyg4ometry.visualisation.VtkViewer()
    v.addLogicalVolume(lv)
    v.view()

It is possible to view the logical volume with an offset (i.e. translation) and
rotation. This is purely for adding the scene of the viewer and does not affect
the logical volume itself or anything it is used in. We can see the docstring:

>>> v = pyg4ometry.visualisation.VtkViewer()
>>> v.addLogicalVolume?
Signature:
v.addLogicalVolume(
logical,
mtra=matrix([[1, 0, 0],
[0, 1, 0],
[0, 0, 1]]),
tra=array([0, 0, 0]),
recursive=True,
)

If we start from a rotation as a series of Tait-Bryan angles, we can turn this into
a matrix with:

.. code-block::

   import numpy as np
   rotation = [0, np.pi/2, 0] # for example
   matrix = np.linalg.inv(pyg4ometry.transformation.tbxyz2matrix(rotation))
   l # a pyg4ometry.geant4.LogicalVolume instance
   v = pyg4ometry.visualisation.VtkViewer()
   v.addLogicalVolume(l, mtra=rotation, tra=[0,0,500])


.. note::
   When directly using rotations and translations, the units are radians and mm.

If overlap checking has been used, this produces overlap meshes (if any) and these will
be visualised automatically when visualising a LogicalVolume instance as they are associated
with that instance.

Solid
-----

It is possible to view an individual solid, i.e. any instance of a class in
:code:`pyg4ometry.geant4.solid` module.

.. code-block:: python

    s  # e.g. a pyg4ometry.geant4.solid.Box instance
    v = pyg4ometry.visualisation.VtkViewer()
    v.addSolid(s)
    v.view()


Similarly to a logical volume, an individual solid has no concept of placement position
and will by default be placed at the centre of the scene. It is also possible to add it
to the scene with a rotation and translation.

>>> v.addSolid?
Signature:
v.addSolid(
solid,
rotation=[0, 0, 0],
position=[0, 0, 0],
representation='surface',
colour=[0.5, 0.5, 0.5],
opacity=0.2,
)

This uses Tait-Bryan angles for the rotation.

Boolean Solid
-------------

When creating geometry, it is common to use Boolean operations. Sometimes, we make mistakes
in these and it is useful to understand the individual constituents even if the result is not
a valid solid or mesh (i.e. completely disconnected solids). To do this we can visualise just
a Boolean solid on its own.

.. code-block::

   s # e.g. a pyg4ometry.geant4.solid.Subtraction instance
   v = pyg4ometry.visualisation.VtkViewer()
   v.addBooleanSolidRecursive(s)
   v.view()

This will work recursively for each solid that makes up the Boolean even if they are Booleans
themselves. It will tolerate shapes that cannot form a valid mesh such as the resultant Boolean
solid.

Default Colour Coding
---------------------

With the :code:`VtkViewer` class all volumes are visualised as semi-transparent grey.

Custom Colour Coding
--------------------

With the :code:`VtkViewerColoured` class, we can provide a default general colour and also
a dictionary of specific colours for materials by name.

Random Colours
--------------

With the :code:`VtkViewerColoured` class, we can supply the default colour as :code:`"random"`,
which will result in every volume being visualised with a random colour to be different.

.. code-block::

   v = pyg4ometry.visualisation.VtkViewerColoured(defaultColour="random")


Overlaying Two Geometries
-------------------------

In the visualiser we add "meshes" to the scene that are displayed. We are not restricted to
make a physically accurate model and we can draw multiple meshes on top of each other by
successively adding them to the scene.

Logical Volume Difference
*************************

The function :code:`pyg4ometry.visualisation.viewLogicalVolumeDifference` is provided that will
view two :code:`pyg4ometry.geant4.LogicalVolume` instances. It will also calculate the difference
mesh between the two and visualise that also on top of the two with a different colour to highlight it.

Viewing FLUKA geometry
----------------------

The viewer can be used to view FLUKA geometry.

.. code-block::

    r = pyg4ometry.fluka.Reader("./FLUKA_FILE.inp")
    v = pyg4ometry.visualisation.VtkViewerNew()
    v.addFlukaRegions(r.getRegistry())
    v.buildPipelinesAppend()
    v.view()