#!/bin/bash

for RUNDIR in /mnt/hds/proj/bioinfo/DEMUX/*CCXX; do
    echo $RUNDIR;
    for LANE in 1 2 3 4 5 6 7 8; do
        ls -l ${RUNDIR}/l${LANE}t*/Project*/Sample_*/*.fastq.gz > $RUNDIR/${LANE}.index.stats.txt

        echo "sbatch -A prod001 -t 10:00:00 -c 1 -e /mnt/hds/proj/bioinfo/LOG/undetermined-%j.err -o /mnt/hds/proj/bioinfo/LOG/undetermined-%j.out undetermined.batch $RUNDIR $LANE"
        sbatch -A prod001 -t 10:00:00 -c 1 -e /mnt/hds/proj/bioinfo/LOG/undetermined-%j.err -o /mnt/hds/proj/bioinfo/LOG/undetermined-%j.out undetermined.batch $RUNDIR $LANE
    done;
done

for RUNDIR in /mnt/hds2/proj/bioinfo/DEMUX/*CCXX; do
    echo $RUNDIR;
    for LANE in 1 2 3 4 5 6 7 8; do
        ls -l ${RUNDIR}/l${LANE}t*/*/*/*.fastq.gz > $RUNDIR/${LANE}.index.stats.txt

        echo "sbatch -A prod001 -t 10:00:00 -c 1 -e /mnt/hds/proj/bioinfo/LOG/undetermined-%j.err -o /mnt/hds/proj/bioinfo/LOG/undetermined-%j.out undetermined.batch $RUNDIR $LANE"
        sbatch -A prod001 -t 10:00:00 -c 1 -e /mnt/hds/proj/bioinfo/LOG/undetermined-%j.err -o /mnt/hds/proj/bioinfo/LOG/undetermined-%j.out undetermined.batch $RUNDIR $LANE
    done;
done
