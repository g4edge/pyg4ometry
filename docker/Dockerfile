FROM ubuntu:jammy

USER root
WORKDIR /root

# configure system
COPY . /root
RUN apt-get update -qq && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    DEBIAN_FRONTEND="noninteractive" apt-get -y install $(cat packages) && \
    locale-gen en_US.UTF-8 && update-locale && \
    rm -rf /var/lib/apt/lists/* && \
    patch -R /usr/include/opencascade/TDocStd_Application.hxx < patches/TDocStd_Application.patch

ENV LC_ALL="en_US.utf8" \
    LANGUAGE="en_US.utf8" \
    LANG="en_US.utf8"

# default python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
