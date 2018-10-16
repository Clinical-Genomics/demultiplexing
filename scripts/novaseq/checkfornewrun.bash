#!/bin/bash

shopt -s nullglob
shopt -s expand_aliases
source ~/.aliases

########
# VARS #
########

INDIR=${1?'please provide a base dir'}
DEMUX_DIR=${2?'please provide a demux dir'}
SCRIPT_DIR=$(dirname $(readlink -nm $0))
EMAIL=clinical-demux@scilifelab.se

#############
# FUNCTIONS #
#############

log () {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo [${NOW}] $@
}

failed() {
    cat ${PROJECTLOG} | mail -s "ERROR starting X demultiplexing" $EMAIL
}
trap failed ERR

########
# MAIN #
########

for RUNDIR in ${INDIR}/*; do
    RUN=$(basename ${RUNDIR})

    if [[ -f ${RUNDIR}/RTAComplete.txt ]]; then
        if [[ ! -f ${RUNDIR}/demuxstarted.txt ]]; then
            if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
                log "${RUN} fetching samplesheet.csv"
                FC=${RUN##*_}
                demux sheet fetch --application all ${FC} > ${RUNDIR}/SampleSheet.csv
            fi
            log "${RUN} starting demultiplexing"
            date +'%Y%m%d%H%M%S' > ${RUNDIR}/demuxstarted.txt

            mkdir -p ${DEMUX_DIR}/${RUN}/
            PROJECTLOG=${DEMUX_DIR}/${RUN}/projectlog.$(date +'%Y%m%d%H%M%S').log
            bash ${SCRIPT_DIR}/demux-novaseq.bash ${RUNDIR} ${DEMUX_DIR} &>> ${PROJECTLOG}
            rm -f ${DEMUX_DIR}/copycomplete.txt
        else
            log "${RUN} is finished and demultiplexing has already started"
        fi
    else
        log "${RUN} is not finished yet"
    fi
done
