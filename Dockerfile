FROM quay.io/fenicsproject/stable:current
LABEL maintainer="Mehdi Saraeian <mehdi@iastate.edu>"

USER root

ENV DEBIAN_FRONTEND=noninteractive

######################
# Python information #
######################
RUN which python3
RUN python3 -c 'import sys; print(sys.version_info[:])'
RUN pip install --upgrade pip

######################
# tIGAr Installation #
######################

RUN pip install git+https://github.com/blechta/tsfc.git@2018.1.0
RUN pip install git+https://github.com/blechta/COFFEE.git@2018.1.0
RUN pip install git+https://github.com/blechta/FInAT.git@2018.1.0
RUN pip install singledispatch==3.7.0 networkx==2.5.1 pulp==2.7.0
RUN pip install git+https://github.com/MehdiSaraeian/tIGAr.git@32c7f0296fb171a5a8dc91ea3120218f85630a19
RUN pip install git+https://github.com/dalcinl/igakit.git@1a9c7a494c2c403e921a968efeba4637dc8cc0a1
RUN pip install scipy==1.5.4

#######################
# ShNAPr Installation #
#######################

RUN pip install git+https://github.com/MehdiSaraeian/ShNAPr.git

########################
# VarMINT Installation #
########################

RUN pip install git+https://github.com/MehdiSaraeian/VarMINT.git

###########################
# CouDALFISh Installation #
###########################

RUN pip install git+https://github.com/MehdiSaraeian/CouDALFISh.git
