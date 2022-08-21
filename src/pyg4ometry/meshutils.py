import numpy as _np

def MeshShrink(m, shrinkFactor = 1e-5) :
    verts = m[0]
    facet = m[1]

    vertnormals = []
    nvertnormals = []

    for i in range(0,len(verts)) : 
        vertnormals.append([0,0,0])
        nvertnormals.append(0)

    for tri in facet : 
        
        i1 = tri[0]
        i2 = tri[1]
        i3 = tri[2]

        v1 = _np.array(verts[i1])
        v2 = _np.array(verts[i2])
        v3 = _np.array(verts[i3])
        
        e1 = v1-v1
        e2 = v2-v1
        e3 = v3-v1

        normal = _np.cross(e2,e3)
        normal = normal/_np.linalg.norm(normal)

        vertnormals[i1][0] = vertnormals[i1][0] + normal[0]
        vertnormals[i1][1] = vertnormals[i1][1] + normal[1]
        vertnormals[i1][2] = vertnormals[i1][2] + normal[2]

        vertnormals[i2][0] = vertnormals[i2][0] + normal[0]
        vertnormals[i2][1] = vertnormals[i2][1] + normal[1]
        vertnormals[i2][2] = vertnormals[i2][2] + normal[2]

        vertnormals[i3][0] = vertnormals[i3][0] + normal[0]
        vertnormals[i3][1] = vertnormals[i3][1] + normal[1]
        vertnormals[i3][2] = vertnormals[i3][2] + normal[2]
        
        nvertnormals[i1] = nvertnormals[i1] + 1
        nvertnormals[i2] = nvertnormals[i2] + 1
        nvertnormals[i3] = nvertnormals[i3] + 1

    
    for i in range(0,len(vertnormals)) : 
        vertnormalmag     = _np.sqrt(vertnormals[i][0]**2 + vertnormals[i][1]**2 + vertnormals[i][2]**2)
        vertnormals[i][0] = vertnormals[i][0]/nvertnormals[i]/vertnormalmag
        vertnormals[i][1] = vertnormals[i][1]/nvertnormals[i]/vertnormalmag
        vertnormals[i][2] = vertnormals[i][2]/nvertnormals[i]/vertnormalmag
         # print vertnormalmag, vertnormals[i]
        
    for i in range(0,len(verts)) :
        verts[i][0] = verts[i][0] - shrinkFactor*vertnormals[i][0]
        verts[i][1] = verts[i][1] - shrinkFactor*vertnormals[i][1]
        verts[i][2] = verts[i][2] - shrinkFactor*vertnormals[i][2]

    m.append(vertnormals)
        
    return vertnormals
