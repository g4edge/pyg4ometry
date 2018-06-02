#include <cmath>
#include <vector>
#include <utility>
#include "Vector.h"

inline double rad2deg(double rad){
  return (rad/M_PI)*180.;
}

inline double deg2rad(double deg){
  return (deg/180.)*M_PI;
}

inline std::vector<std::vector<double> > MatrixMult(std::vector<std::vector<double> >& m1,std::vector<std::vector<double> >& m2){
  std::vector<std::vector<double> > mout(m1.size(),std::vector<double>(m2[0].size(),0.0)); 
  for(int i=0;i<mout.size();i++){
    for(int j=0;j<mout[i].size();j++){
      for(int k=0;k<m1[i].size();k++){
        mout[i][j] += m1[i][k]*m2[k][j];
      }  
    }
  }
  return mout;
}

std::pair<Vector,double> tbxyz(Vector* rv){
  double sx = sin(rv->x());
  double cx = cos(rv->x());
  double sy = sin(rv->y());
  double cy = cos(rv->y());
  double sz = sin(rv->z());
  double cz = cos(rv->z());

  //3D Rotation matrices
  std::vector<std::vector<double> > mx(3,std::vector<double>(3));
  std::vector<std::vector<double> > my(3,std::vector<double>(3));
  std::vector<std::vector<double> > mz(3,std::vector<double>(3));

  mx[0][0] = 1.;mx[0][1] = 0.;mx[0][2] = 0.;
  mx[1][0] = 0.;mx[1][1] = cx;mx[1][2] =-sx;
  mx[2][0] = 0.;mx[2][1] = sx;mx[2][2] = cx;

  my[0][0] = cy;my[0][1] = 0.;my[0][2] = sy;
  my[1][0] = 0.;my[1][1] = 1.;my[1][2] = 0.;
  my[2][0] =-sy;my[2][1] = 0.;my[2][2] = cy;

  mz[0][0] = cz;mz[0][1] =-sz;mz[0][2] = 0.;
  mz[1][0] = sz;mz[1][1] = cz;mz[1][2] = 0.;
  mz[2][0] = 0.;mz[2][1] = 0.;mz[2][2] = 1.;

  std::vector<std::vector<double> > mzmy = MatrixMult(mz,my);
  std::vector<std::vector<double> > m = MatrixMult(mzmy,mx);

  // Angle of rotation
  double ang = acos((m[0][0]+m[1][1]+m[2][2]-1)/2.0);

  // Axis of rotation
  Vector axi;
  if(ang == 0.){
    axi = Vector(0.0,0.0,1.0);
  }
  else if(ang > 0.0 && ang < M_PI){
    double denom = 2.0*std::abs(sin(ang));
    axi = Vector((m[2][1]-m[1][2])/denom,(m[0][2]-m[2][0])/denom,(m[1][0]-m[0][1])/denom);
  }
  else{
    if (m[0][0] > m[1][1] && m[0][0] > m[2][2]){
      axi = Vector(m[0][0]+1,m[0][1],m[0][2]);
    }
    else if(m[1][1] > m[0][0] && m[1][1] > m[2][2]){
      axi = Vector(m[1][0],m[1][1]+1,m[1][2]);
    } 
    else if(m[2][2] > m[0][0] && m[2][2] > m[1][1]){
      axi = Vector(m[2][0],m[2][1],m[2][2]+1);
    }
    axi = axi.unit(); 
  }

  return std::make_pair(axi,ang);
}


