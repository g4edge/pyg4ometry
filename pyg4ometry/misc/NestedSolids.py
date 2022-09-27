import pyg4ometry.geant4.solid.Box as _box

def NestedBoxes(nameBase, bx,by,bz,registry, lunit="mm", dx=0,dy=0 ,dz=0,N=0) :
    '''
    Creates a list of geant4.Box starting the bx, by, bz in size and each element is dx, dy, dz smaller
    for each iteration

    :param nameBase: name stub for solid
    :type nameBase: str
    :param bx: box max x size
    :type bx: float
    :param by: box max y size
    :type by: float
    :param bz: box max z size
    :type bz: float
    :param registry: Registry object
    :type registry: Registry
    :param lunit: length unit (mm/m etc)
    :type lunit: str
    :param dx: decrement in x for each iteration
    :type dx: float
    :param dy: decrement in y for each iteration
    :type dy: float
    :param dz: decrement in z for each iteration
    :type dz: float
    :param N: number of iterations
    :type N: int
    '''

    solids = []

    for i in range(0,N+1,1) :
        nameLevel = nameBase+"_"+str(i)
        b = _box(nameLevel,bx-i*dx,by-i*dy,bz-i*dz,registry,lunit)
        solids.append(b)

    return solids
