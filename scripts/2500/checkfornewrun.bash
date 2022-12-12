#!/bin/bash

shopt -s nullglob
CONDA_EXE="/home/proj/production/bin/miniconda3/bin/conda"
DEMUX_ENV_NAME="P_demux"

INDIR=${1?'please provide a run dir'}
DEMUXDIR=${2?'please provide a demux dir'}

for RUNDIR in ${INDIR}/*; do
    RUN=$(basename ${RUNDIR})
    NOW=$(date +"%Y%m%d%H%M%S")
    if [[ -f ${RUNDIR}/RTAComplete.txt ]]; then
        if [[ ! -f ${RUNDIR}/demuxstarted.txt ]]; then
            if grep -qs '<Read Number="1" NumCycles="36" IsIndexedRead="N" />' ${RUNDIR}/runParameters.xml; then
                echo [${NOW}] ${RUN} is NIPT - skipping
                continue
            fi
            if [[ ! -e ${RUNDIR}/SampleSheet.ctmr ]]; then
                if grep -qs ',ctmr,' ${RUNDIR}/SampleSheet.csv; then
                    echo [${NOW}] ${RUN} is CTMR - transmogrifying SampleSheet.csv
                    cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/SampleSheet.ctmr
                    ${CONDA_EXE} run --name $DEMUX_ENV_NAME demux sheet demux -a miseq ${RUNDIR}/SampleSheet.ctmr > ${RUNDIR}/SampleSheet.csv
                    cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/Data/Intensities/BaseCalls/
                fi
            fi
            if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
                echo [${NOW}] ${RUN} fetching samplesheet.csv
                FC=${RUN##*_}
                FC=${FC:1}
                ${CONDA_EXE} run --name $DEMUX_ENV_NAME demux sheet fetch --application wes --shortest ${FC} > ${RUNDIR}/SampleSheet.csv
                cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/Data/Intensities/BaseCalls/
            else
                echo converting ${RUNDIR}/SampleSheet.csv
                ${CONDA_EXE} run --name $DEMUX_ENV_NAME demux sheet convert ${RUNDIR}/SampleSheet.csv > ${RUNDIR}/SampleSheet.conv
                cp ${RUNDIR}/SampleSheet.conv ${RUNDIR}/SampleSheet.csv
                cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/Data/Intensities/BaseCalls/
            fi
            echo [${NOW}] ${RUN} starting demultiplexing
            bash /home/proj/production/bin/git/demultiplexing/scripts/2500/demux-2500.bash ${RUNDIR} ${DEMUXDIR}
            rm ${DEMUXDIR}/copycomplete.txt
        else
            echo [${NOW}] ${RUN} is finished and demultiplexing has already started - demuxstarted.txt exists
        fi
    else
        echo [${NOW}] ${RUN} is not finished yet
    fi
done
