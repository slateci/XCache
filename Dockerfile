# FROM opensciencegrid/atlas-xcache:fresh
FROM opensciencegrid/atlas-xcache:upcoming-fresh

LABEL maintainer Ilija Vukotic <ivukotic@cern.ch>

# adding user group atlas access rights (read and list)
RUN echo "g /atlas / rl" > /etc/xrootd/auth_db; \
    touch /etc/xrootd/xcache.cfg /var/run/x509up

# not sure this line is needed
RUN mkdir -p /xrd/var/log /xrd/var/spool /xrd/var/run /tests


COPY runme.sh run_x509_updater.sh /usr/local/sbin/
COPY xcache.cfg /etc/xrootd/
RUN chmod +x /usr/local/sbin/run_x509_updater.sh

# not sure the two lines bellow are needed at all
# if needed change ownership of directories
RUN if [ $(stat -c "%U:%G" /xrd/var ) != "xrootd:xrootd" ]; then chown -R xrootd:xrootd /xrd/var; fi
RUN if [ $(stat -c "%U:%G" /xrd ) != "xrootd:xrootd" ]; then chown -R xrootd:xrootd /xrd; fi

# build  
RUN echo "Timestamp:" `date --utc` | tee /image-build-info.txt

CMD [ "/usr/local/sbin/runme.sh" ]
