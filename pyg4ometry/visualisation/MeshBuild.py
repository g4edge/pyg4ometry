import vtk


def quadric(lower, upper, *,
            cxx=0, cyy=0, czz=0,
            cxy=0, cyz=0, cxz=0,
            cx=0, cy=0, cz=0,
            c=0,
            capping=False, vtkCleanPolyData=True):
    """Make a vtk Quadric Surface polydata mesh.
    lower: lower bound in which to generate the surface mesh
    upper: upper bound in which to generate teh surface mesh
    capping: whether to cap the open mesh.
    vtkCleanPolyData: whether to apply the vtkCleaPolyData filter to the mesh.

    """

    quadric = vtk.vtkQuadric()
    quadric.SetCoefficients(cxx, cyy, czz,
                            cxy, cyz, cxz,
                            cx,  cy, cz,
                            c)

    sample = vtk.vtkSampleFunction()
    # sample.SetSampleDimensions(50, 50, 50)
    sample.SetSampleDimensions(75, 75, 75)

    sample.SetModelBounds(lower[0], upper[0],
                          lower[1], upper[1],
                          lower[2], upper[2])


    sample.SetImplicitFunction(quadric)
    if capping:
        sample.SetCapping(1)


    # Make the mesh, generating a single contour at F(x, y, z) = 0.
    contours = vtk.vtkContourFilter()
    contours.SetInputConnection(sample.GetOutputPort())
    contours.GenerateValues(1, 0, 0)
    pipeline = contours

    if vtkCleanPolyData:
        # Deal with facets which are zero-area facets (i.e. lines).
        cleaner = vtk.vtkCleanPolyData()
        cleaner.SetInputConnection(contours.GetOutputPort())
        cleaner.ConvertLinesToPointsOn()
        cleaner.Update()
        pipeline = cleaner

    polydata = pipeline.GetOutput()

    return polydata
