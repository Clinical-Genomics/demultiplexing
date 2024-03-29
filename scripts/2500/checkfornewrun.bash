#!/bin/bash

shopt -s nullglob
source "${HOME}/.bashrc"
shopt -s expand_aliases

INDIR=${1?'please provide a run dir'}
DEMUXDIR=${2?'please provide a demux dir'}
ENVIRONMENT=${3?'please provide the environment'}

if [[ ${ENVIRONMENT} == 'production' ]]; then
    useprod
    SLURM_ACCOUNT=production
elif [[ ${ENVIRONMENT} == 'stage' ]]; then
    usestage
    SLURM_ACCOUNT=development
fi


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
                    demux sheet demux -a miseq ${RUNDIR}/SampleSheet.ctmr > ${RUNDIR}/SampleSheet.csv
                    cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/Data/Intensities/BaseCalls/
                fi
            fi
            if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
                echo [${NOW}] ${RUN} fetching samplesheet.csv
                FC=${RUN##*_}
                FC=${FC:1}
                demux sheet fetch --application wes --shortest ${FC} > ${RUNDIR}/SampleSheet.csv
                cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/Data/Intensities/BaseCalls/
            else
                echo converting ${RUNDIR}/SampleSheet.csv
                demux sheet convert ${RUNDIR}/SampleSheet.csv > ${RUNDIR}/SampleSheet.conv
                cp ${RUNDIR}/SampleSheet.conv ${RUNDIR}/SampleSheet.csv
                cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/Data/Intensities/BaseCalls/
            fi
            echo [${NOW}] ${RUN} starting demultiplexing
            bash "/home/proj/${ENVIRONMENT}/bin/git/demultiplexing/scripts/2500/demux-2500.bash" ${RUNDIR} ${DEMUXDIR}
            rm ${DEMUXDIR}/copycomplete.txt
        else
            echo [${NOW}] ${RUN} is finished and demultiplexing has already started - demuxstarted.txt exists
        fi
    else
        echo [${NOW}] ${RUN} is not finished yet
    fi
done
