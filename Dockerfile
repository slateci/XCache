FROM centos:latest

LABEL maintainer Ilija Vukotic <ivukotic@cern.ch>


RUN mkdir -p /etc/grid-security/certificates /etc/grid-security/vomsdir /etc/grid-security/xrd /data

RUN yum -y update

RUN yum install -y \
    curl \
    gperftools \
    hostname   

# for CA certificates
RUN yum localinstall https://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm -y

RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm; \
    curl -s -o /etc/pki/rpm-gpg/RPM-GPG-KEY-wlcg http://linuxsoft.cern.ch/wlcg/RPM-GPG-KEY-wlcg; \
    curl -s -o /etc/yum.repos.d/wlcg-centos7.repo http://linuxsoft.cern.ch/wlcg/wlcg-centos7.repo; \
    curl -s -o /etc/yum.repos.d/xrootd-stable-slc7.repo http://www.xrootd.org/binaries/xrootd-stable-slc7.repo
RUN yum install -y xrootd-server xrootd-client xrootd vomsxrd
RUN yum install -y xrootd-rucioN2N-for-Xcache
RUN yum install -y supervisor fetch-crl 


RUN yum install -y \
    python-pip \
    python36 \
    jq

RUN pip install --upgrade pip
RUN pip install --no-cache-dir \
    requests

# python3
RUN python36 -m ensurepip
RUN pip3.6 install --upgrade pip
RUN pip3.6 install --no-cache-dir \
    requests


# setup supervisord
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


RUN echo "g /atlas / rl" > /etc/xrootd/auth_db; \
    touch /etc/xrootd/xcache.cfg /var/run/x509up

# not sure this line is needed
RUN mkdir -p /data/xrd/namespace /data/xrd/xrdcinfos /data/xrd/datafiles /data/xrd/var/log /data/xrd/var/spool /data/xrd/var/run

COPY xcache_limits.conf /etc/security/limits.d
COPY xcache.cfg /etc/xrootd/
COPY runme.sh run_cache_reporter.sh run_x509_updater.sh cacheReporter/reporter.py /
RUN chmod 755 /runme.sh /run_cache_reporter.sh /run_x509_updater.sh /reporter.py

RUN mkdir /tests
COPY tests/* /tests/
RUN chmod 755 /tests/stress_test.sh

# xrootd user is created during installation
# here we will fix its GID and UID so files created by one container will be modifiable by the next.
RUN groupmod -o -g 10940 xrootd
RUN usermod -o -u 10940 -g 10940 -s /bin/sh xrootd

# not sure the two lines bellow are needed at all
# if needed change ownership of directories
RUN if [ $(stat -c "%U:%G" /data/xrd/var ) != "xrootd:xrootd" ]; then chown -R xrootd:xrootd /data/xrd/var; fi
RUN if [ $(stat -c "%U:%G" /data/xrd ) != "xrootd:xrootd" ]; then chown -R xrootd:xrootd /data/xrd; fi

# build  
RUN echo "Timestamp:" `date --utc` | tee /image-build-info.txt

CMD [ "/runme.sh" ]

# CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf", "-n"]