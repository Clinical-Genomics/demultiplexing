FROM centos:7

RUN yum update -y \
   && yum install -y unzip

# Log into basespace and download the .rmp zip file. Place it in the same dir as the dockerfile
COPY bcl2fastq2-v2-20-0-linux-x86-64.zip /tmp

##### Get and install bcl2fastq
RUN cd /tmp \
    && unzip bcl2fastq2-v2-20-0-linux-x86-64.zip \
    && yum install -y bcl2fastq2-v2.20.0.422-Linux-x86_64.rpm
RUN rm /tmp/bcl2fastq2*

