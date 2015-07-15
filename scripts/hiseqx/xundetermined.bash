#!/bin/bash

VERSION=3.18.1

RUNDIR=$1
echo $RUNDIR;
for LANE in 1 2 3 4 5 6 7 8; do
    ls -l ${RUNDIR}/l${LANE}t*/*/*/Und*R1*.fastq.gz > $RUNDIR/${LANE}.index.stats.txt

    echo "sbatch -A prod001 -t 10:00:00 -c 1 --mail-user=kenny.billiau@scilifelab.se --mail-type=END -e /mnt/hds/proj/bioinfo/LOG/undetermined-%j.err -o /mnt/hds/proj/bioinfo/LOG/undetermined-%j.out undetermined.batch $RUNDIR $LANE"
    sbatch -A prod001 -t 10:00:00 -c 1 --mail-user=kenny.billiau@scilifelab.se --mail-type=END -e /mnt/hds/proj/bioinfo/LOG/undetermined-%j.err -o /mnt/hds/proj/bioinfo/LOG/undetermined-%j.out xundetermined.batch $RUNDIR $LANE
done;
