#!/bin/bash

shopt -s nullglob

INDIR=${1-'/home/clinical/RUNS/'}
DEMUXDIR=${2-'/home/clinical/DEMUX/'}

for RUNDIR in ${INDIR}/*; do
    RUN=$(basename ${RUNDIR})
    NOW=$(date +"%Y%m%d%H%M%S")
    if [[ -f ${RUNDIR}/RTAComplete.txt ]]; then
        if [[ ! -f ${RUNDIR}/demuxstarted.txt ]]; then
            if grep -qs '<Read Number="1" NumCycles="36" IsIndexedRead="N" />' ${RUNDIR}/runParameters.xml; then
                echo [${NOW}] ${RUN} is NIPT - skipping
                continue
            fi
            echo [${NOW}] ${RUN} is finished but demultiplexing has not started
            demuxproccount=$(ps aux | grep HISEQ | grep grep -v | wc | awk '{print $1}')
            if [[ "${demuxproccount}" -lt 15 ]]; then
                echo [${NOW}] ${RUN} starting demultiplexing
                bash /home/clinical/SCRIPTS/demux.bash ${RUNDIR} ${DEMUXDIR} &
            else
                echo [${NOW}] ${RUN} did not start demultiplexing other processes running
            fi
        else
            echo [${NOW}] ${RUN} is finished and demultiplexing has already started - started.txt exists
        fi
    else
        echo [${NOW}] ${RUN} is not finished yet
    fi
done
