#!/bin/bash

apt-get -y update
apt-get -y install libboost-dev libcgal-dev libgmp-dev libmpfr-dev \
           libvtk9-dev libxi-dev libocct-*-dev occt-misc

root_version="6.28.04"
ROOTSYS="$HOME/.local"

mkdir -p "$ROOTSYS"
wget -q -O- "https://root.cern/download/root_v${root_version}.Linux-ubuntu22-x86_64-gcc11.3.tar.gz" \
    | tar --strip-components 1 -C /opt/root --strip=1 -x -z

PATH="$PATH:$ROOTSYS/bin"
LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$ROOTSYS/lib"
MANPATH="$MANPATH:$ROOTSYS/man"
PYTHONPATH="$PYTHONPATH:$ROOTSYS/lib"
JUPYTER_CONFIG_DIR="$JUPYTER_CONFIG_DIR:$ROOTSYS/etc/notebook"
CLING_STANDARD_PCH="none"
export ROOTSYS PATH LD_LIBRARY_PATH MANPATH JUPYTER_CONFIG_DIR CLING_STANDARD_PCH

if [ -n "$GITHUB_ENV" ]; then
    {
        echo "ROOTSYS=\"$ROOTSYS\""
        echo "PATH=\"\$PATH:$ROOTSYS/bin\""
        echo "LD_LIBRARY_PATH=\"\$LD_LIBRARY_PATH:$ROOTSYS/lib\""
        echo "MANPATH=\"\$MANPATH:$ROOTSYS/man\""
        echo "PYTHONPATH=\"\$PYTHONPATH:$ROOTSYS/lib\""
        echo "JUPYTER_CONFIG_DIR=\"\$JUPYTER_CONFIG_DIR:$ROOTSYS/etc/notebook\""
        echo "CLING_STANDARD_PCH=none"
    } >> "$GITHUB_ENV"
fi
