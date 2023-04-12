#!/bin/bash

apt-get -y update
apt-get -y install libboost-dev libcgal-dev libgmp-dev libmpfr-dev \
           libocct-* libtbb-dev libvtk9-dev occt-misc

patch -R /usr/include/opencascade/TDocStd_Application.hxx < docker/patches/TDocStd_Application.patch
