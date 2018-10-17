#!/bin/bash

set -u

shopt -s nullglob
shopt -s expand_aliases
source ~/.aliases

########
# VARS #
########

IN_DIR=${1?'please provide the runs dir'}
DEMUXES_DIR=${2?'please provide the demuxes dir'}
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

for RUN_DIR in ${IN_DIR}/*; do
    if [[ ! -d ${RUN_DIR} ]]; then
        continue
    fi

    RUN=$(basename ${RUN_DIR})
    FC=${RUN##*_}
    FC=${FC:1}

    if [[ -f ${RUN_DIR}/RTAComplete.txt ]]; then
        if [[ ! -f ${RUN_DIR}/demuxstarted.txt ]]; then
            log "date +'%Y%m%d%H%M%S' > ${RUN_DIR}/demuxstarted.txt"
            date +'%Y%m%d%H%M%S' > ${RUN_DIR}/demuxstarted.txt

            if [[ ! -e ${RUN_DIR}/SampleSheet.csv ]]; then
                log "demux sheet fetch --application all ${FC} > ${RUN_DIR}/SampleSheet.csv"
                demux sheet fetch --application all ${FC} > ${RUN_DIR}/SampleSheet.csv
            fi

            log "mkdir -p ${DEMUXES_DIR}/${RUN}/"
            mkdir -p ${DEMUXES_DIR}/${RUN}/

            PROJECTLOG=${DEMUXES_DIR}/${RUN}/projectlog.$(date +'%Y%m%d%H%M%S').log
            log "bash ${SCRIPT_DIR}/demux-novaseq.bash ${RUN_DIR} ${DEMUXES_DIR} &>> ${PROJECTLOG}"
            bash ${SCRIPT_DIR}/demux-novaseq.bash ${RUN_DIR} ${DEMUXES_DIR} &>> ${PROJECTLOG}

            log "rm -f ${DEMUXES_DIR}/${RUN}copycomplete.txt"
            rm -f ${DEMUXES_DIR}/${RUN}/copycomplete.txt
            log "date +'%Y%m%d%H%M%S' > ${DEMUXES_DIR}/${RUN}/demuxcomplete.txt"
            date +'%Y%m%d%H%M%S' > ${DEMUXES_DIR}/${RUN}/demuxcomplete.txt
        else
            log "${RUN} is finished and demultiplexing has already started"
        fi
    else
        log "${RUN} is not finished yet"
    fi
done
