#!/bin/bash

yum updateinfo
yum -y install boost-devel gmp-devel mpfr-devel OCE-* tbb-devel vtk-devel

# cgal not in the centos repos
wget http://springdale.princeton.edu/data/springdale/7/x86_64/os/Computational/CGAL-4.11.1-1.sdl7.x86_64.rpm
wget http://springdale.princeton.edu/data/springdale/7/x86_64/os/Computational/CGAL-devel-4.11.1-1.sdl7.x86_64.rpm
yum install -y CGAL-4.11.1-1.sdl7.x86_64.rpm CGAL-devel-4.11.1-1.sdl7.x86_64.rpm 

patch -R /usr/include/opencascade/TDocStd_Application.hxx < docker/patches/TDocStd_Application.patch
