#!/bin/bash

VERSION=3.42.0
echo "$0 VERSION $VERSION"

RUNDIR=$1
SCRIPTDIR=/mnt/hds/proj/bioinfo/SCRIPTS/
LOGDIR=${RUNDIR}/LOG/

[[ ! -e ${LOGDIR} ]] && mkdir ${LOGDIR}

echo $RUNDIR;
FC=$( basename `dirname ${RUNDIR}/SampleSheet.csv` | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
for LANE in 1 2 3 4 5 6 7 8; do
    ls -l ${RUNDIR}/l${LANE}t*/Und*R1*.fastq.gz > ${LOGDIR}/${LANE}.index.stats.txt

    echo "zgrep ^@ST ${RUNDIR}/l${LANE}t*/Undetermined*R1*.fastq.gz | cut -d: -f 11 | sort | uniq -c | sort -nr >> $LOGDIR/${LANE}.index.stats.txt"
    zgrep ^@ST ${RUNDIR}/l${LANE}t*/Undetermined*R1*.fastq.gz | awk -F ':' '{print $NF}' | sort | uniq -c | sort -nr >> ${LOGDIR}/${LANE}.index.stats.txt
done;
