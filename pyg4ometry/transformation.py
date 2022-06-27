import numpy as _np

def rad2deg(rad) :
    '''Convert rad in radians into degrees

    :param rad: Input in radians
    :type rad: float
    :return: rad in degrees
    :rtype: float

    '''

    return 180 * (rad / _np.pi)

def deg2rad(deg) :
    '''Convert deg in degrees into radians

    :param deg: Input in degrees
    :type deg: float
    :return: deg in radians
    :rtype: float

    '''

    return _np.pi * (deg / 180.)

def grad2rad(gradians) :
    '''Convert rad in gradians into radians

    :param gradians: Input in gradians
    :type gradians: float
    :return: gradians in radians
    :rtype: float

    '''

    return _np.pi * (gradians / 200.)

def tbxyz2axisangle(rv) :
    '''
    Tait-Bryan x-y-z rotation to axis-angle representation
    Algorithm from http://www.sedris.org/wg8home/Documents/WG80485.pdf

    For converting rotation angles to an active axis/angle pair for
    use in pycsg.  Order of rotation:  x->y->z.

    :param rv: rotation angles
    :type rv: float(3)
    :returns: [axis,angle]
    :rtype: list(list(3),float)

    '''
    matrix = tbxyz2matrix(rv)
    return matrix2axisangle(matrix)


def matrix2axisangle(matrix):

    '''
    Convert 3x3 transformation matrix to axis angle representation

    :param matrix: 3x3 rotation matrix array
    :type matrix: array(3,3)
    :returns: [axis,angle]
    :rtype: list(list(3),float)

    '''

    m = matrix
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
    else :
        if m[0,0] > m[1,1] and m[0,0] > m[2,2] :
            axi = _np.array([m[0,0]+1,m[0,1],m[0,2]])
        elif m[1,1] > m[0,0] and m[1,1] > m[2,2] :
            axi = _np.array([m[1,0],m[1,1]+1,m[1,2]])
        elif m[2,2] > m[0,0] and m[2,2] > m[1,1] :
            axi = _np.array([m[2,0],m[2,1],m[2,2]+1])

        axi = axi/_np.sqrt((axi*axi).sum())
    return [list(axi),ang]

def axisangle2matrix(axis, angle):

    '''
    Convert axis angle to transformation matrix

    :param axis: axis for rotation
    :type axis: list/array(3)
    :param angle: rotation angle
    :type angle: float
    :returns: transformation matrix
    :rtype: array(3,3)

    '''

    axis = [i/_np.linalg.norm(axis) for i in axis]
    cos = _np.cos(angle)
    sin = _np.sin(angle)
    versin = 1 - cos
    x = axis[0]
    y = axis[1]
    z = axis[2]

    a_11 = (versin * x * x) + cos
    a_12 = (versin * x * y) - (z * sin)
    a_13 = (versin * x * z) + (y * sin)

    a_21 = (versin * y * x) + (z * sin)
    a_22 = (versin * y * y) + cos
    a_23 = (versin * y * z) - (x * sin)

    a_31 = (versin * z * x) - (y * sin)
    a_32 = (versin * z * y) + (x * sin)
    a_33 = (versin * z * z) + cos

    return  _np.array([[a_11, a_12, a_13],
                        [a_21, a_22, a_23],
                        [a_31, a_32, a_33]])

def matrix2tbxyz(matrix):
    """
    Convert rotation matrix to Tait-Bryan angles.
    Order of rotation is x -> y -> z.

    :param matrix: active (positive angle = anti-clockwise rotation about that axis when looking at the axis) matrix.

    :return: [x, y, z] Tait-Bryan angles in a list.
    :rtype: list(3)
    """

    a_11 = matrix[0,0]
    a_12 = matrix[0,1]
    a_13 = matrix[0,2]
    a_21 = matrix[1,0]
    a_31 = matrix[2,0]
    a_32 = matrix[2,1]
    a_33 = matrix[2,2]

    if _np.isclose(a_31, 1) and a_31 > 1.0:
        a_31 = 1.0
    elif _np.isclose(a_31, -1) and a_31 < -1.0:
        a_31 = -1.0

    if abs(a_31) != 1:
        x = _np.arctan2(a_32, a_33)
        y = _np.arcsin(-a_31)
        z = _np.arctan2(a_21, a_11)
    elif a_31 == -1:
        y = _np.pi / 2.0
        z = 0.0
        x = _np.arctan2(a_12, a_13) + z
    elif a_31 == +1:
        y = -_np.pi / 2.0
        z = 0.0
        x = _np.arctan2(-a_12, -a_13) - z

    return [x, y, z]

def axisangle2tbxyz(axis, angle):
    """
    Convert axis and angle to tait bryan angles

    :param axis: axis for rotation
    :type axis: list/array(3)
    :param angle: rotation angle
    :type angle: float
    :returns: tait bryan angles (x-y-z)
    :rtype: array(3)

    """


    return matrix2tbxyz(axisangle2matrix(axis, angle))

def tbxyz2matrix(angles):
    """
    Convert tait bryan angles to a single passive rotation matrix.
    rotation order = x -> y -> z.
    
    :param angles: list of angles:  x, y, z

    :return: rotation matrix
    :rtype: array(3,3)
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

    # Rotation matrices.
    mx = _np.array([[1,    0,    0],
                     [0,   cx,  -sx],
                     [0,  sx,    cx]])
    my = _np.array([[ cy,  0,   sy],
                     [  0,  1,    0],
                     [-sy,   0,  cy]])
    mz = _np.array([[ cz, -sz,  0],
                     [ sz,  cz,  0],
                     [  0,   0,  1]])

    m = mz.dot(my.dot(mx))
    return m

def tbzyx2matrix(angles):
    """
    Convert Tait-Bryan angles to a single passive rotation matrix.
    rotation order = x -> y -> z.
    
    :param angles: list of angles:  x, y, z

    :return: rotation matrix
    :rtype: array(3,3)

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

    # Rotation matrices.
    mx = _np.array([[1,    0,    0],
                     [0,   cx,  -sx],
                     [0,  sx,    cx]])
    my = _np.array([[ cy,  0,   sy],
                     [  0,  1,    0],
                     [-sy,   0,  cy]])
    mz = _np.array([[ cz, -sz,  0],
                     [ sz,  cz,  0],
                     [  0,   0,  1]])

    m = mx.dot(my.dot(mz))
    return m

def matrix_from(v_from, v_to):
    """
    Returns the rotation matrix that rotates v_from to parallel to
    v_to.

    Useful for ensuring a given face points in a certain
    direction.

    v_from and v_to should be array-like three-vectors.

    """
    # Trivial cases that the algorithm otherwise can't handle:
    if are_parallel(v_from, v_to):
        return _np.array(_np.eye(3))
    elif are_anti_parallel(v_from, v_to):
        return _rodrigues_anti_parallel(v_from, v_to)
    # Get the axis to rotate around and the angle to rotate by:
    axis = (_np.cross(v_from,
                      v_to)
            / _np.linalg.norm(_np.cross(v_from,
                                        v_to)))
    angle = _np.arccos(_np.dot(v_from,
                               v_to)
                       / (_np.linalg.norm(v_from)
                          * _np.linalg.norm(v_to)))

    # Construct the skew-symmetric cross product matrix.
    cross_matrix = _np.array([[0,       -axis[2],  axis[1]],
                               [axis[2],       0,  -axis[0]],
                               [-axis[1], axis[0],        0]])
    # Rodrigues' rotation formula.
    rotation_matrix = (_np.eye(3)
                       + (_np.sin(angle) * (cross_matrix))
                       + ((1 - _np.cos(angle))
                          * (cross_matrix).dot(cross_matrix)))

    assert are_parallel(v_to, rotation_matrix.dot(v_from)), (
        "Not parallel!")
    assert _np.allclose(rotation_matrix.T.dot(rotation_matrix), _np.eye(3)), (
        "Not orthogonal!")
    return rotation_matrix

def _rodrigues_anti_parallel(v_from, v_to):
    """
    v_from = vector FROM
    v_to = vector TO

    source:
    http://en.citizendium.org/wiki/Rotation_matrix#Case_that_.22from.22_and_.22to.22_vectors_are_anti-parallel
    """

    v_from_mag = _np.linalg.norm(v_from)
    v_to_mag = _np.linalg.norm(v_to)

    v_from = [v_i / v_from_mag for v_i in v_from]
    v_to = [v_i / v_to_mag for v_i in v_to]

    # Handle case when vector is along the z-axis:
    if _np.allclose(abs(v_from[2]), 1.0):
        return _np.array([[-1, 0, 0],
                           [ 0, 1, 0],
                           [ 0, 0, -1]])

    # First row
    R_11 = -(v_from[0]**2 - v_from[1]**2)
    R_12 = -2 * v_from[0] * v_from[1]
    R_13 = 0.

    # Second row:
    R_21 = R_12
    R_22 = -1 * R_11
    R_23 = 0.

    # Third row:
    R_31 = 0.0
    R_32 = 0.0
    R_33 = -(1 - v_from[2]**2)

    factor = 1 / (1 - v_from[2]**2)

    rotation_matrix = factor * _np.array([[R_11, R_12, R_13],
                                           [R_21, R_22, R_23],
                                           [R_31, R_32, R_33]])

    assert are_parallel(v_to, rotation_matrix.dot(v_from)), (
        "Not parallel!")
    assert _np.allclose(rotation_matrix.T.dot(rotation_matrix), _np.eye(3)), (
        "Not orthogonal!")

    return rotation_matrix

def are_parallel(vector_1, vector_2, tolerance=1e-10):
    """
    Check if vector vector_1 is parallel to vector vector_2 down to
    some tolerance.

    :param vector_1: First input vector
    :type vector_1: array
    :param vector_2: Second input vector
    :type vector_2: array
    :param tolerance: Tolerance for calculation
    :type tolerance: float
    :returns: if vectors are parallel
    :rtype: bool

    """
    return (_np.dot(vector_1, vector_2) / (_np.linalg.norm(vector_1)
                                           * _np.linalg.norm(vector_2))
            > 1 - tolerance)

def are_anti_parallel(vector_1, vector_2, tolerance=1e-10):
    """
    Check if vector vector_1 is parallel to vector vector_2 down to
    some tolerance.

    :param vector_1: First input vector
    :type vector_1: array
    :param vector_2: Second input vector
    :type vector_2: array
    :param tolerance: Tolerance for calculation
    :type tolerance: float
    :returns: if vectors are antiparallel
    :rtype: bool
    """
    return (_np.dot(vector_1, vector_2) / (_np.linalg.norm(vector_1)
                                          * _np.linalg.norm(vector_2))
            < -1 + tolerance)

def reverse(angles):
    """
    Invert the rotation represented by these angles.

    """
    # Convert to matrix, invert, and then convert back to angles
    return matrix2tbxyz(tbxyz2matrix(angles).T)

def two_fold_orientation(v1, v2, e1, e2):
    """ matrix_from will align one vector with another, but there are
    an infinite number of such matrices that align two vectors.  This
    further contrains the rotation by introducing a second pair of vectors.

    v1 start v
    v2 end v
    e1 start e
    e2 end v
    """
    m1 = matrix_from(v1, v2)
    m2 = matrix_from(m1.dot(e1), e2)
    return m2.dot(m1)

