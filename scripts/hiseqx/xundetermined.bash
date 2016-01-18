#!/bin/bash

VERSION=3.34.1
echo "$0 VERSION $VERSION"

RUNDIR=$1
SCRIPTDIR=/mnt/hds/proj/bioinfo/SCRIPTS/
LOGDIR=${RUNDIR}/LOG/

[[ ! -e ${LOGDIR} ]] && mkdir ${LOGDIR}

echo $RUNDIR;
FC=$( basename `dirname ${RUNDIR}/SampleSheet.csv` | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
for LANE in 1 2 3 4 5 6 7 8; do
    ls -l ${RUNDIR}/l${LANE}t*/*/*/Und*R1*.fastq.gz > ${LOGDIR}/${LANE}.index.stats.txt

    echo "sbatch -A prod001 -t 10:00:00 -c 1 -J 'xundetermined-${FC}' --mail-user=kenny.billiau@scilifelab.se --mail-type=END -e /mnt/hds/proj/bioinfo/LOG/undetermined-%j.err -o /mnt/hds/proj/bioinfo/LOG/undetermined-%j.out $SCRIPTDIR/undetermined.batch $RUNDIR $LANE"
    sbatch -A prod001 -t 10:00:00 -c 1 -J "xundetermined-${FC}" --mail-user=kenny.billiau@scilifelab.se --mail-type=END -e /mnt/hds/proj/bioinfo/LOG/undetermined-%j.err -o /mnt/hds/proj/bioinfo/LOG/undetermined-%j.out $SCRIPTDIR/xundetermined.batch $RUNDIR $LANE
done;
