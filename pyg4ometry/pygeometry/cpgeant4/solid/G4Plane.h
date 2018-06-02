#ifndef G4PLANE_H
#define G4PLANE_H
#include "CSGMesh.h"
#include "Solids.h"
#include "SolidBase.h"
#include "Vector.h"
#include <cmath>

class G4Plane : public SolidBase{
public:
    G4Plane(std::string name, Vector* _normal,double _dist, double _zlength=10000):
            SolidBase(name,"G4Plane"),normal(_normal),dist(_dist),zlength(_zlength){
        SetMesh(CSGMesh::ConstructPlane(normal,dist,zlength));
    }
    const double dist,zlength;
    Vector* normal;
};

#endif
