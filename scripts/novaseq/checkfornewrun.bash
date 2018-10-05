#!/bin/bash

shopt -s nullglob
shopt -s expand_aliases
source ~/.aliases

INDIR=${1?'please provide a run dur'}
DEMUXDIR=${2?'please provide a demux dir'}

for RUNDIR in ${INDIR}/*; do
    RUN=$(basename ${RUNDIR})
    NOW=$(date +"%Y%m%d%H%M%S")
    if [[ -f ${RUNDIR}/RTAComplete.txt ]]; then
        if [[ ! -f ${RUNDIR}/demuxstarted.txt ]]; then
            if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
                echo [${NOW}] ${RUN} fetching samplesheet.csv
                FC=${RUN##*_}
                demux sheet fetch --application all ${FC} > ${RUNDIR}/SampleSheet.csv
            fi
            echo [${NOW}] ${RUN} starting demultiplexing
            bash /home/hiseq.clinical/SCRIPTS/demux-novaseq.bash ${RUNDIR} ${DEMUXDIR}
            rm ${DEMUXDIR}/copycomplete.txt
        else
            echo [${NOW}] ${RUN} is finished and demultiplexing has already started - started.txt exists
        fi
    else
        echo [${NOW}] ${RUN} is not finished yet
    fi
done
