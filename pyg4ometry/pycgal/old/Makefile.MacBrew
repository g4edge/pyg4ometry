CXX=g++

%.o : %.cpp
	$(CXX) -std=c++14 -fPIC -c $< -I/usr/local/include

pyg4_cgal.so : pyg4_cgal.o
	$(CXX) -shared -o $@ $< -I/usr/local/include -L/usr/local/lib/ -lmpfr -lgmp -lboost_thread-mt -lstdc++

clean : 
	rm -rf *.o *.so *.pyc *~

polyhedron_load : polyhedron_load.cpp
	$(CXX) -o $@ polyhedron_load.cpp -I/usr/local/include -L/usr/local/lib/ -lmpfr -lgmp -lboost_thread-mt -lstdc++