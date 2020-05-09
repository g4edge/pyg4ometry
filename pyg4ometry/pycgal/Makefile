CXX=clang++

PWD = $(shell pwd)

CGAL_INCLUDES = -I/opt/local/include
CGAL_LIBS     = -L/opt/local/lib/ -lCGAL -lmpfr -lgmp -lboost_thread-mt

PYTHON_INCLUDES  = $(shell python3 -m pybind11 --includes)
PYTHON_EXTENSION = $(shell python3-config --extension-suffix)
PYTHON_LIBRARY   = $(shell python3-config --ldflags)

%.o : %.cpp
	$(CXX) -std=c++14 -fPIC -c $< -I/opt/local/include

pyg4_cgal$(PYTHON_EXTENSION) : pyg4_cgal.o
	$(CXX) -shared -o $@ $< -I/opt/local/include -L/opt/local/lib/ -lCGAL -lmpfr -lgmp -lboost_thread-mt -lstdc++

clean : 
	rm -rf *.o *.so *.pyc *~

polyhedron_load : polyhedron_load.cpp
	$(CXX) -o $@ polyhedron_load.cpp -I/usr/local/include -L/usr/local/lib/ -lmpfr -lgmp -lboost_thread-mt -lstdc++

cgal : geom$(PYTHON_EXTENSION) core$(PYTHON_EXTENSION) algo$(PYTHON_EXTENSION)

geom$(PYTHON_EXTENSION) : geom.cxx geom.h
	$(CXX) -O3 -Wall -shared -std=c++11 -fPIC $(PYTHON_INCLUDES) -o $@ $< $(PYTHON_LIBRARY) 

core$(PYTHON_EXTENSION) : core.cxx core.h
	$(CXX) -O3 -Wall -shared -std=c++11 -fPIC $(PYTHON_INCLUDES) -o $@ $< $(PYTHON_LIBRARY) geom$(PYTHON_EXTENSION)	
	install_name_tool -change geom$(PYTHON_EXTENSION) @rpath/geom$(PYTHON_EXTENSION) core$(PYTHON_EXTENSION)
	install_name_tool -add_rpath $(PWD) core$(PYTHON_EXTENSION)

algo$(PYTHON_EXTENSION) : algo.cxx algo.h
	$(CXX) -O3 -Wall -shared -std=c++11 -fPIC $(PYTHON_INCLUDES) $(CGAL_INCLUDES) -o $@ $< $(PYTHON_LIBRARY) geom$(PYTHON_EXTENSION) core$(PYTHON_EXTENSION) $(CGAL_LIBS)
	install_name_tool -change geom$(PYTHON_EXTENSION) @rpath/geom$(PYTHON_EXTENSION) algo$(PYTHON_EXTENSION)
	install_name_tool -change core$(PYTHON_EXTENSION) @rpath/core$(PYTHON_EXTENSION) algo$(PYTHON_EXTENSION)
	install_name_tool -add_rpath $(PWD) algo$(PYTHON_EXTENSION)
