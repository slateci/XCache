FROM centos:latest

LABEL maintainer Ilija Vukotic <ivukotic@cern.ch>


RUN mkdir -p /etc/grid-security/certificates /etc/grid-security/vomsdir /etc/grid-security/xrd

RUN yum -y update

RUN yum install -y \
    curl \
    gperftools \
    hostname   

# for CA certificates
RUN yum localinstall https://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm -y

RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm; \
    curl -s -o /etc/pki/rpm-gpg/RPM-GPG-KEY-wlcg http://linuxsoft.cern.ch/wlcg/RPM-GPG-KEY-wlcg; \
    curl -s -o /etc/yum.repos.d/wlcg-centos7.repo http://linuxsoft.cern.ch/wlcg/wlcg-centos7.repo; 

RUN echo $'[xrootd-experimental]\nname=XRootD Experimental\nbaseurl=http://storage-ci.web.cern.ch/storage-ci/xrootd/experimental/epel-7/x86_64\ngpgcheck=0\nenabled=1' >  /etc/yum.repos.d/xrootd-experimental-slc7.repo

RUN yum install -y xrootd-server xrootd-client xrootd vomsxrd
RUN yum install -y xrootd-rucioN2N-for-Xcache
RUN yum install -y supervisor fetch-crl 

RUN wget -r -nH -nd -np -R "index.html*" http://xrd-cache-1.t2.ucsd.edu/RPMS/rhel7-cksum/
RUN yum -y update *.rpm


RUN yum install -y \
    python-pip \
    python36 \
    jq

RUN pip install --upgrade pip
RUN pip install  --upgrade requests

# python3
RUN python36 -m ensurepip
RUN pip3.6 install --upgrade pip
RUN pip3.6 install --upgrade requests


# setup supervisord
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


RUN echo "g /atlas / rl" > /etc/xrootd/auth_db; \
    touch /etc/xrootd/xcache.cfg /var/run/x509up

# not sure this line is needed
RUN mkdir -p /xrd/var/log /xrd/var/spool /xrd/var/run

COPY xcache_limits.conf /etc/security/limits.d
COPY xcache.cfg /etc/xrootd/
COPY runme.sh run_cache_reporter.sh run_x509_updater.sh cacheReporter/reporter.py updateAGISstatus.sh /
# RUN chmod 755 /runme.sh /run_cache_reporter.sh /run_x509_updater.sh /reporter.py /updateAGISstatus.sh

RUN mkdir /tests
COPY tests/* /tests/
# RUN chmod 755 /tests/stress_test.sh
# RUN chmod 755 /tests/stress_test.from_es.sh

# xrootd user is created during installation
# here we will fix its GID and UID so files created by one container will be modifiable by the next.
RUN groupmod -o -g 10940 xrootd
RUN usermod -o -u 10940 -g 10940 -s /bin/sh xrootd

# not sure the two lines bellow are needed at all
# if needed change ownership of directories
RUN if [ $(stat -c "%U:%G" /xrd/var ) != "xrootd:xrootd" ]; then chown -R xrootd:xrootd /xrd/var; fi
RUN if [ $(stat -c "%U:%G" /xrd ) != "xrootd:xrootd" ]; then chown -R xrootd:xrootd /xrd; fi

# build  
RUN echo "Timestamp:" `date --utc` | tee /image-build-info.txt

CMD [ "/runme.sh" ]

# CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf", "-n"]