.. _loading:

================
Loading Geometry
================

Generally, a reader class is provided for each format. The reader is created, then told to
load a file, and it creates a Registry object (see :ref:`introduction-registry`) containing
the model. The registry is the final object from a reader, and its top-most volume can be
used for visualisation or other operations.

Here, we use example files provided in the g4edge-testdata package that can be installed with:
::

    pip install g4edge-testdata


An instance of the test data can be used to access any file.

.. tab:: GDML

  .. code-block:: python
    :linenos:

    import pyg4ometry
    import g4edgetestdata

    d = g4edgetestdata.G4EdgeTestData()
    r = pyg4ometry.gdml.Reader(d["gdml/ChargeExchangeMC/lht.gdml"])
    l = r.getRegistry().getWorldVolume()
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(l)
    v.view()

  .. figure:: figures/viewing-gdml.png
      :width: 80%
      :align: center

      Geant4 example GDML from ChargeExchangeMC example.

.. tab:: FLUKA

  **Note** FLUKA geometry can be loaded but cannot be visualised directly without
  conversion to a Geant4 model. This is not necessary for simiply loading, but it is
  shown here.

  .. code-block:: python
    :linenos:

    import pyg4ometry
    import g4edgetestdata

    d = g4edgetestdata.G4EdgeTestData()
    r = pyg4ometry.fluka.Reader(d["fluka/ex-geometry.inp"])
    flukaRegistry = r.flukaregistry

    geantRegistry = pyg4ometry.convert.fluka2Geant4(flukaRegistry)

    l = geantRegistry.getWorldVolume()
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(l)
    v.view()

  .. figure:: figures/viewing-fluka.png
      :width: 80%
      :align: center

      FLUKA example.

.. tab:: ROOT

  .. code-block:: python
    :linenos:

    import pyg4ometry
    import g4edgetestdata

    d = g4edgetestdata.G4EdgeTestData()
    r = pyg4ometry.io.ROOTTGeo.Reader(d["root/lht.root"])
    l = r.getRegistry().getWorldVolume()
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(l)
    v.view()

  .. figure:: figures/viewing-root.png
      :width: 80%
      :align: center

      ROOT example of Geant4's LHT geometry.


.. tab:: STL

  STL files are typically used for a single watertight solid mesh. This mesh is
  converted to a TesselatedSolid and then a logical volume which can be placed
  in a geometry.

  .. code-block:: python
    :linenos:

    import pyg4ometry
    import g4edgetestdata

    d = g4edgetestdata.G4EdgeTestData()
    reg = pyg4ometry.geant4.Registry()
    r = pyg4ometry.stl.Reader(d["stl/utah_teapot.stl"], reg)
    s = r.getSolid()
    copper = pyg4ometry.geant4.MaterialPredefined("G4_Cu", reg)
    l = pyg4ometry.geant4.LogicalVolume(s, copper, "utahteapot_lv", reg)
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(l)
    v.view()

  .. figure:: tutorials/tutorial2.png
        :width: 80%
        :align: center
        :alt: Example of STL loading in pyg4ometry

        Example of STL loading in pyg4ometry. Pressing :code:`s` on the keyboard
        when in the visualiser will switch to solid mode. :code:`w`, conversely will
        switch to wireframe.


.. tab:: STEP

  STEP file loading is possible in pyg4ometry. Note, here only a basic loading is shown
  without material assignment, which normally is not information contained in a STEP file
  but is necessary for Geant4 or FLUKA simulations.

  .. code-block:: python
    :linenos:

    import pyg4ometry
    import g4edgetestdata

    d = g4edgetestdata.G4EdgeTestData()
    r = pyg4ometry.pyoce.Reader(d["step/1_BasicSolids_Bodies.step"])
    ls = r.freeShapes()
    worldName = pyg4ometry.pyoce.pythonHelpers.get_TDataStd_Name_From_Label(ls.Value(1))
    mats, skip, mesh = {}, [], {}
    reg = pyg4ometry.convert.oce2Geant4(r.shapeTool, worldName, mats, skip, mesh)
    wl = reg.logicalVolumeDict[worldName]
    v = pyg4ometry.visualisation.VtkViewerColouredMaterial()
    v.addLogicalVolume(wl)
    v.view()

  .. figure:: figures/viewing-step.png
        :width: 80%
        :align: center
        :alt: Example of STEP loading in pyg4ometry

        STEP file loading example in pyg4ometry. Pressing :code:`s` on the keyboard
        when in the visualiser will switch to solid mode. :code:`w`, conversely will
        switch to wireframe.
