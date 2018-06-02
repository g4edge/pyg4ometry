#include "Vector.h"
#include "math.h"

Vector::Vector() 
{
  _x = 0.0;
  _y = 0.0;
  _z = 0.0;
}

Vector::Vector(double xIn, double yIn, double zIn) 
{
  _x = xIn;
  _y = yIn;
  _z = zIn;
}  

Vector::Vector(const Vector &v) 
{
  _x = v._x;
  _y = v._y;
  _z = v._z;
}

double Vector::x() const
{
  return _x;
}

double Vector::y() const
{
  return _y;
}

double Vector::z() const
{
  return _z;
}

Vector Vector::clone() const
{
  return Vector(_x,_y,_z);
}

void Vector::negated()
{
  _x = -_x;
  _y = -_y;
  _z = -_z;
}

Vector Vector::plus(const Vector &rhs) const
{
  return Vector(_x+rhs._x, _y+rhs._y, _z+rhs._z);
}

Vector Vector::operator+(const Vector &rhs) const
{
  return this->plus(rhs);
}

Vector& Vector::operator+=(const Vector &rhs)
{
  this->_x = this->_x + rhs._x;
  this->_y = this->_y + rhs._y;
  this->_z = this->_z + rhs._z;
  return *this;
}

Vector Vector::minus(const Vector &rhs) const
{
  return Vector(_x-rhs._x, _y-rhs._y, _z-rhs._z);
}

Vector Vector::operator-(const Vector &rhs) const
{
  return this->minus(rhs);
}

Vector& Vector::operator-=(const Vector &rhs)
{
  _x -= rhs._x;
  _y -= rhs._y;
  _z -= rhs._z;
  return *this;
}

Vector Vector::times(double a) const
{
  return Vector(a*_x, a*_y, a*_z);
}

Vector Vector::operator*(double a) const
{
  return this->times(a);
}

Vector& Vector::operator*=(double a)
{
  _x *= a;
  _y *= a;
  _z *= a;
  return *this;
}

Vector  Vector::divideBy(double a) const 
{
  return Vector(_x/a,_y/a,_z/a);
}

Vector  Vector::operator/(double a) const
{
  return this->divideBy(a);
}

Vector& Vector::operator/=(double a)
{
  _x /= a;
  _y /= a;
  _z /= a;
  return *this;
}

double Vector::dot(const Vector &rhs) const 
{
  return _x*rhs.x() + _y*rhs.y() + _z*rhs.z();
}

Vector Vector::scale(const Vector &rhs) const
{
  return Vector(_x*rhs.x(), _y*rhs.y(), _z*rhs.z());
}

void Vector::scale(Vector *rhs){
  _x *= rhs->x();
  _y *= rhs->y();
  _z *= rhs->z();
}

Vector Vector::lerp(const Vector &a, double t) const
{
  return this->plus(a.minus(*this).times(t));
}

double Vector::length() const 
{
  return sqrt(this->dot(*this));
}

Vector Vector::unit() const 
{
  return this->divideBy(this->length());
}

Vector Vector::cross(const Vector &rhs) const
{
  return Vector(_y*rhs._z - _z*rhs._y,
		_z*rhs._x - _x*rhs._z,
		_x*rhs._y - _y*rhs._x);
}

double& Vector::operator[](int i) 
{
  if(i==0) 
    return _x;
  else if(i==1)
    return _y;
  else if(i==2)
    return _z;

  return _x;
}

double Vector::operator[](int i) const 
{
  if(i==0) 
    return _x;
  else if(i==1)
    return _y;
  else if(i==2)
    return _z;

  return _x;  
}

Vector operator*(double d, const Vector& rhs) 
{
  return rhs.times(d);
}

std::ostream& operator<<(std::ostream& ostr, const Vector& rhs) 
{
  ostr << rhs.x() << " " << rhs.y() << " " << rhs.z() << std::endl;
  return ostr;
}
