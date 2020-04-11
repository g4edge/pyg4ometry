%.o : %.cpp
	g++ -std=c++11 -fPIC -c $< -I/opt/local/include

pyg4_cgal.so : pyg4_cgal.o
	g++ -shared -o $@ $< -I/opt/local/include -L/opt/local/lib/ -lCGAL -lmpfr -lgmp -lboost_thread-mt -lstdc++

clean : 
	rm -rf *.o *.so *.pyc *~