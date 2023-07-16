import pyg4ometry

def Test(vis=False, interactive=False):
    e = pyg4ometry.fluka.Extruder()

    r1 = e.add_region("outer")
    r1.append([-100, -100])
    r1.append([-100,  100])
    r1.append([100,  100])
    r1.append([100, -100])
    e.set_region_to_outer_boundary("outer")

    r2 = e.add_region("pole")
    r2.append([-50, -50])
    r2.append([-50,  50])
    r2.append([50,  50])
    r2.append([50, -50])

    e.build_cgal_polygons()

    e.plot()


    return e