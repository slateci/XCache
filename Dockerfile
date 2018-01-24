FROM centos:latest

LABEL maintainer "yangw@slac.stanford.edu"

RUN mkdir -p /etc/grid-security/certificates /etc/grid-security/vomsdir /etc/grid-security/xrd /data

RUN yum install -y curl gperftools hostname
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm; \
    curl -s -o /etc/pki/rpm-gpg/RPM-GPG-KEY-wlcg http://linuxsoft.cern.ch/wlcg/RPM-GPG-KEY-wlcg; \
    curl -s -o /etc/yum.repos.d/wlcg-centos7.repo http://linuxsoft.cern.ch/wlcg/wlcg-centos7.repo; \
    curl -s -o /etc/yum.repos.d/xrootd-stable-slc7.repo http://www.xrootd.org/binaries/xrootd-stable-slc7.repo
RUN yum install -y xrootd-server xrootd-client xrootd vomsxrd
RUN yum install -y xrootd-rucioN2N-for-Xcache

RUN echo "g /atlas / rl" > /etc/xrootd/auth_db; \
    touch /etc/xrootd/xcache.cfg /var/run/x509up

COPY xcache.cfg /etc/xrootd/
COPY runme.sh /
RUN chmod 755 /runme.sh

# build info
RUN echo "Timestamp:" `date --utc` | tee /image-build-info.txt

CMD [ "/runme.sh" ]
