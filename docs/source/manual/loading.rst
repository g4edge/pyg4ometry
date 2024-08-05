.. _loading:

================
Loading Geometry
================

Generally, a reader class is provided for each format. The reader is created, then told to
load a file, and it creates a Registry object (see :ref:`introduction-registry`) containing
the model. The registry is the final object from a reader, and its top-most volume can be
used for visualisation or other operations.

.. tab:: GDML

  In directory :code:`pyg4ometry/test/gdmlG4examples/ChargeExchangeMC/`

  .. code-block:: python
    :linenos:

    import pyg4ometry

    r = pyg4ometry.gdml.Reader("lht.gdml")
    l = r.getRegistry().getWorldVolume()
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(l)
    v.view()

  .. figure:: figures/viewing-gdml.png
      :width: 80%
      :align: center

      Geant4 example GDML from ChargeExchangeMC example.

.. tab:: FLUKA

  In directory :code:`pyg4ometry/test/flukaCompoundExamples`

  **Note** FLUKA geometry can be loaded but cannot be visualised directly without
  conversion to a Geant4 model. This is not necessary for loading, but shown here.

  .. code-block:: python
    :linenos:

    import pyg4ometry

    r = pyg4ometry.fluka.Reader("corrector-dipole2.inp")
    flukaRegistry = r.flukaregistry

    geantRegistry = pyg4ometry.convert.fluka2Geant4(flukaRegistry)

    l = geantRegistry.getWorldVolume()
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(l)
    v.view()

  .. figure:: figures/viewing-fluka.png
      :width: 80%
      :align: center

      FLUKA example of a dipole magnet.

.. tab:: ROOT

  In directory :code:`pyg4ometry/test/root2Gdml`

  .. code-block:: python
    :linenos:

    import pyg4ometry

    r = pyg4ometry.io.ROOTTGeo.Reader("example.root")
    l = r.getRegistry().getWorldVolume()
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(l)
    v.view()

  .. figure:: figures/viewing-root.png
      :width: 80%
      :align: center

      ROOT example of Geant4's LHT geometry.


.. tab:: STL

  In directory :code:`pyg4ometry/test/stl`

  STL files are typically used for a single watertight solid mesh. This mesh is
  converted to a TesselatedSolid and then a logical volume which can be placed
  in a geometry. In directory :code:`pyg4ometry/test/stl`.

  .. code-block:: python

    import pyg4ometry

    reg = pyg4ometry.geant4.Registry()
    r = pyg4ometry.stl.Reader("utahteapot.stl", reg)
    s = r.getSolid()
    copper = pyg4ometry.geant4.MaterialPredefined("G4_Cu", reg)
    l = pyg4ometry.geant4.LogicalVolume(s, copper, "utahteapot_lv", reg)
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(l)
    v.view()

  .. figure:: tutorials/tutorial2.png
 :alt: Example of STL loading in pyg4ometry


.. tab:: STEP


  In directory :code:`pyg4ometry/test/freecad`

  .. code-block:: python
    :linenos:

    import pyg4ometry

    r = pyg4ometry.freecad.Reader("08_AshTray.step")
    r.relabelModel()
    r.convertFlat()
    l = r.getRegistry().getWorldVolume()
    v = pyg4ometry.visualisation.VtkViewer()
    v.addLogicalVolume(l)
    v.view()

  .. figure:: tutorials/tutorial3.png
      :alt: Example of STEP loading in pyg4ometry
