all : _Vector.so _Vertex.so _Polygon.so _Plane.so _BSPNode.so _CSG.so _Solids.so _VertsAndPolys.so boolTest


boolTest : csg.so boolTest.o
	g++ -framework CoreFoundation -o $@ boolTest.o ./csg.so

csg.so : Vector.o Vertex.o Polygon.o Plane.o BSPNode.o CSG.o Solids.o 
	g++ -shared -framework CoreFoundation -o csg.so $? -L/opt/local/lib/ -lpython2.7

_VertsAndPolys.so : VertsAndPolys_wrap.o csg.so
	g++ -shared -framework CoreFoundation VertsAndPolys_wrap.o ./csg.so -L/opt/local/lib/ -lpython2.7 -o $@

_Solids.so : Solids_wrap.o csg.so
	g++ -shared -framework CoreFoundation Solids_wrap.o ./csg.so -L/opt/local/lib/ -lpython2.7 -o $@

_BSPNode.so : BSPNode_wrap.o csg.so
	g++ -shared -framework CoreFoundation BSPNode_wrap.o ./csg.so -L/opt/local/lib/ -lpython2.7 -o $@

_CSG.so : CSG_wrap.o csg.so
	g++ -shared -framework CoreFoundation CSG_wrap.o ./csg.so -L/opt/local/lib/ -lpython2.7 -o $@

_Plane.so : Plane_wrap.o csg.so
	g++ -shared -framework CoreFoundation Plane_wrap.o ./csg.so  -L/opt/local/lib/ -lpython2.7 -o $@

_Polygon.so : Polygon_wrap.o csg.so
	g++ -shared -framework CoreFoundation Polygon_wrap.o ./csg.so -L/opt/local/lib/ -lpython2.7 -o $@

_Vertex.so : Vertex_wrap.o csg.so
	g++ -shared -framework CoreFoundation Vertex_wrap.o ./csg.so -L/opt/local/lib/ -lpython2.7 -o $@

_Vector.so : Vector_wrap.o csg.so
	g++ -shared -framework CoreFoundation Vector_wrap.o ./csg.so -L/opt/local/lib/ -lpython2.7 -o $@

%.o : %.C
	g++ -g -std=c++11 -O2 -fPIC -c $< -I./

%.o : %.c
	g++ -g -std=c++11 -O2 -fPIC -c $< -I./

%.o : %.cxx
	g++ -g -std=c++11 -O2 -fPIC -c $< -I/opt/local/Library/Frameworks/Python.framework/Versions/2.7/include/python2.7/

%_wrap.cxx : %.i %.h
	swig -c++ -python -shadow $<

clean :
	rm -rf *.so *.o *_wrap.cxx *.pyc

