#!/bin/bash

apt-get -y update
apt-get -y install libboost-dev libcgal-dev libgmp-dev libmpfr-dev \
           libvtk9-dev libxi-dev libocct-*-dev occt-misc
