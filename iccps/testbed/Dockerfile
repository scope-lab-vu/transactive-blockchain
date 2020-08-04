FROM ubuntu:18.04

# RUN export FNCS_INSTALL="$HOME/FNCS-install"

# build-essential : required for building fncs
# autoconf : required to configure gridlab-d
# libtool : required for fncs(?), gridlab-d
# libxerces-c-dev : not required for this demo, but required to fully build gridlab-d
# pyzmq, numpy : required by te30 demo
RUN apt-get update \
    && apt-get install -y \
    build-essential \
    autoconf \
    libtool \
    libxerces-c-dev \
    git \
    tmux \
    libzmq3-dev \
    libczmq-dev \
    python3-pip \
    && pip3 install pyzmq \
    && pip3 install numpy \
    && cd \
    && git clone https://github.com/FNCS/fncs \
    && cd fncs \
    && git checkout develop \
    && export FNCS_INSTALL="/usr/local" \
    && ./configure --prefix=$FNCS_INSTALL --with-zmq=$FNCS_INSTALL \
    && make \
    && make install \
    && cd \
    && git clone https://github.com/gridlab-d/gridlab-d \
    && cd gridlab-d \
    && autoreconf -fi \
    && ./configure --with-fncs=$FNCS_INSTALL --enable-silent-rules 'CFLAGS=-g -O0 -w' 'CXXFLAGS=-g -O0 -w' 'LDFLAGS=-g -O0 -w' \
    && make \
    && make install \
    && cd \
    && git clone https://github.com/Iceegan/te30_modified.git \
    && cd te30_modified 
 


CMD ["/bin/bash"]