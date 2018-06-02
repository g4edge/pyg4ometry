/* File : example.i */
%module Vector

%{
#include "Vector.h"
%}


%ignore operator[];
%ignore operator<<;

/* Let's just grab the original header file here */
%include "Vector.h"

%extend Vector {
  char*   __str__() const {
    static char tmp[1024];
    sprintf(tmp,"Vector(%g,%g,%g)", $self->x(),$self->y(),$self->z());
    return tmp;    
  }

  char*   __repr__() const {
    static char tmp[1024];
    sprintf(tmp,"Vector(%g,%g,%g)", $self->x(),$self->y(),$self->z());
    return tmp;    
  }

  Vector __rmul__(double a) const {
    return $self->times(a);
  }

  double __getitem__(int i) {
    return $self->operator[](i);
  }

  double __setitem__(int i, double d) {
    return $self->operator[](i) = d;
  }

  Vector __neg__() {
    return Vector(0,0,0)-*$self;
  }
};

