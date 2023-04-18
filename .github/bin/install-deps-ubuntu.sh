#!/bin/bash

apt-get -y update
apt-get -y install libboost-dev libcgal-dev libgmp-dev libmpfr-dev \
           libtbb-dev libvtk9-dev libxi-dev libocct-* occt-misc

# this is certainly needed for jammy (OCE v7.5) and certainly not needed in v7.7 anymore
# not sure about v7.6
patch -R /usr/include/opencascade/TDocStd_Application.hxx < .github/patches/TDocStd_Application.patch
