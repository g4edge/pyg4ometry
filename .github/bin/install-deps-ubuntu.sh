#!/bin/bash

apt-get -y update || exit 1
apt-get -y install libboost-dev libcgal-dev libgmp-dev libmpfr-dev \
           libvtk9-dev libxi-dev libocct-*-dev occt-misc numdiff || exit 1

root_version="6.28.10"
ROOTSYS="/opt/root"

mkdir -p "$ROOTSYS" || exit 1
wget -q -O- "https://root.cern/download/root_v${root_version}.Linux-ubuntu22-x86_64-gcc11.4.tar.gz" \
    | tar --strip-components 1 -C "$ROOTSYS" --strip=1 -x -z || exit 1
