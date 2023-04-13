#!/bin/bash

apt-get -y update
apt-get -y install libboost-dev libcgal-dev libgmp-dev libmpfr-dev \
           libtbb-dev libvtk9-dev libxi-dev libocct-* occt-misc

patch -R /usr/include/opencascade/TDocStd_Application.hxx < .github/patches/TDocStd_Application.patch
