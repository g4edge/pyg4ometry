import numpy as _np

def rad2deg(rad) :
    return rad/_np.pi*180

def deg2rad(deg) :
    return deg/180*_np.pi

def tbxyz(rv) :
    """
    Tait-Bryan x-y-z rotation to axis-angle representation
    Algorithm from http://www.sedris.org/wg8home/Documents/WG80485.pdf

    A positive value corresponds to a clockwise rotation looking
    AT/against the direction of the axis.  This is "left hand rule",
    albeit in a right handed coordinate system.

    rv = list of three angles corresponding to [x, y, z] in radians.

    """
    x = rv[0]
    y = rv[1]
    z = rv[2]
    sx = _np.sin(x)
    cx = _np.cos(x)
    sy = _np.sin(y)
    cy = _np.cos(y)
    sz = _np.sin(z)
    cz = _np.cos(z)

    # Rotation matrices for rotations about the 3 axis:
    mx = _np.matrix([[1,   0,   0],
                     [0,  cx, -sx],
                     [0,  sx,  cx]])
    my = _np.matrix([[ cy,  0, sy],
                     [  0,  1,  0],
                     [-sy,  0, cy]])
    mz = _np.matrix([[ cz, -sz,  0],
                     [ sz,  cz,  0],
                     [  0,   0,  1]])

    m = mz * my * mx

    # angle of rotation
    ang = _np.arccos((float(m.trace())-1)/2.0)

    # axis of rotation
    if ang == 0 :
        axi = _np.array([0,0,1])
    elif ang > 0 and ang < _np.pi :
        axi = _np.array([float(m[2,1]-m[1,2]),
                         float(m[0,2]-m[2,0]),
                         float(m[1,0]-m[0,1])])
        axi = axi / (2*_np.abs(_np.sin(ang)))
    else : # if ang == pi
        if m[0,0] > m[1,1] and m[0,0] > m[2,2] :
            axi = _np.array([m[0,0]+1,m[0,1],m[0,2]])
        elif m[1,1] > m[0,0] and m[1,1] > m[2,2] :
            axi = _np.array([m[1,0],m[1,1]+1,m[1,2]])
        elif m[2,2] > m[0,0] and m[2,2] > m[1,1] :
            axi = _np.array([m[2,0],m[2,1],m[2,2]+1])

        axi = axi/_np.sqrt((axi*axi).sum())
    return [list(axi),ang]

def matrix2tbxyz(matrix):
    """
    Convert rotation matrix to Tait-Bryan angles.

    Order of rotation is x -> y -> z.

    Parameters
    ----------

    matrix : "Orientation" matrix in the form of a numpy matrix instance or
    appropriately formed list.

    Returns:  [x, y, z] Tait-Bryan angles in a list.
    """

    # Get the pertinent elements from the matrix:
    a_11 = matrix[0,0]
    a_12 = matrix[0,1]
    a_13 = matrix[0,2]
    a_21 = matrix[1,0]
    a_23 = matrix[1,2]
    a_31 = matrix[2,0]
    a_32 = matrix[2,1]
    a_33 = matrix[2,2]

    if abs(a_13) != 1:
        x = _np.arctan2(a_23, a_33)
        y = _np.arcsin(-a_13)
        z = _np.arctan2(a_12, a_11)
    elif a_13 == -1:
        x = _np.arctan2(a_21, a_31)
        y = +_np.pi / 2
        z = 0.0
    elif a_13 == +1:
        x = _np.arctan2(-a_21, -a_31)
        y = -_np.pi/2
        z = 0.0

    return [x,y,z]

def tbxyz2matrix(angles):
    """
    Convert Tait Bryan angles to a single passive rotation matrix.
    Rotation order = x -> y -> z.

    Parameters
    ----------
    angles : list of angles:  x, y, z

    Returns: rotation matrix
    """
    x = angles[0]
    y = angles[1]
    z = angles[2]
    sx = _np.sin(x)
    cx = _np.cos(x)
    sy = _np.sin(y)
    cy = _np.cos(y)
    sz = _np.sin(z)
    cz = _np.cos(z)


    # Orientation matrices.  These are transposes of the convential
    # rotation matrices.
    mx = _np.matrix([[1,    0,    0],
                     [0,   cx,   sx],
                     [0,  -sx,   cx]])
    my = _np.matrix([[ cy,  0,  -sy],
                     [  0,  1,    0],
                     [sy,   0,   cy]])
    mz = _np.matrix([[ cz, sz,  0],
                     [ -sz,  cz,  0],
                     [  0,   0,  1]])

    m = mx * my * mz
    return m

def relative_rotation(rot1, rot2):
    """
    Get the relative Tait-Bryan rotation of the second with respect to
    the first.

    """

    # Euler angles aren't vectors so can't casually add/subtract them, you
    # have to convert them back to matrices (or quarternions).  Here:  matrices.

    matrix1 = tbxyz2matrix(rot1)
    matrix2 = tbxyz2matrix(rot2)

    # Sanity check they're orthogonal...
    assert _np.allclose(matrix1.T.dot(matrix1), _np.eye(3)), "matrix is not orthogonal"
    assert _np.allclose(matrix2.T.dot(matrix2), _np.eye(3)), "matrix is not orthogonal"

    # Get the matrix that takes us from rot1 to rot2.
    relative_matrix = matrix1.T * matrix2

    # Get the euler angles from this rotation matrix.
    return matrix2tbxyz(relative_matrix)
