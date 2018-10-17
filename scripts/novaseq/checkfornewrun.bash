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
#EMAIL=clinical-demux@scilifelab.se
EMAIL=kenny.billiau@scilifelab.se

#############
# FUNCTIONS #
#############

log () {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo [${NOW}] $@
}

failed() {
    cat ${PROJECTLOG} | mail -s "ERROR starting novaseq ${FC} on $(hostname)" $EMAIL
}
trap failed ERR

########
# MAIN #
########

for RUNDIR in ${INDIR}/*; do
    if [[ ! -d ${RUNDIR} ]]; then
        continue
    fi

    RUN=$(basename ${RUNDIR})
    FC=${RUN##*_}

    if [[ -f ${RUNDIR}/RTAComplete.txt ]]; then
        if [[ ! -f ${RUNDIR}/demuxstarted.txt ]]; then
            if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
                log "demux sheet fetch --application all ${FC} > ${RUNDIR}/SampleSheet.csv"
                demux sheet fetch --application all ${FC} > ${RUNDIR}/SampleSheet.csv
            fi
            log "date +'%Y%m%d%H%M%S' > ${RUNDIR}/demuxstarted.txt"
            date +'%Y%m%d%H%M%S' > ${RUNDIR}/demuxstarted.txt

            log "mkdir -p ${DEMUX_DIR}/${RUN}/"
            mkdir -p ${DEMUX_DIR}/${RUN}/
            PROJECTLOG=${DEMUX_DIR}/${RUN}/projectlog.$(date +'%Y%m%d%H%M%S').log
            log "bash ${SCRIPT_DIR}/demux-novaseq.bash ${RUNDIR} ${DEMUX_DIR} &>> ${PROJECTLOG}"
            #bash ${SCRIPT_DIR}/demux-novaseq.bash ${RUNDIR} ${DEMUX_DIR} &>> ${PROJECTLOG}

            log "rm -f ${DEMUX_DIR}/copycomplete.txt"
            rm -f ${DEMUX_DIR}/copycomplete.txt
            log "date > ${OUT_DIR}/demuxcomplete.txt"
            date > ${OUT_DIR}/demuxcomplete.txt
        else
            log "${RUN} is finished and demultiplexing has already started"
        fi
    else
        log "${RUN} is not finished yet"
    fi
done
