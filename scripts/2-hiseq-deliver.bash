#!/bin/bash

set -eu
shopt -s nullglob

VERSION=3.4.3

########
# VARS #
########

INDIR=${1-/home/hiseq.clinical/DEMUX/}
TARGET_SERVER=${2-hasta.scilifelab.se}
TARGET_DIR=${3-/home/proj/production/demultiplexed-runs/}
EMAILS=${4-clinical-demux@scilifelab.se}

#############
# FUNCTIONS #
#############

log() {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] $@"
}

#########
# TRAPS #
#########

failed() {
    NAS=$(hostname)
    echo "Error while sending ${RUN} to ${TARGET_SERVER}" | mail -s "Error while sending ${RUN} to ${TARGET_SERVER}" ${EMAILS}
    if [[ ! -z ${RUNDIR} ]]; then
        rm ${RUNDIR}/copycomplete.txt
    fi
}
trap failed ERR

########
# MAIN #
########

for RUNDIR in ${INDIR}/*; do
    RUN=$(basename ${RUNDIR})

    if [[ ! -e ${RUNDIR}/demuxcomplete.txt ]]; then
        log "${RUN} not finished"
        continue
    fi

    if [[ ! -e ${RUNDIR}/copycomplete.txt ]]; then
        date +'%Y%m%d%H%M%S' > ${RUNDIR}/copycomplete.txt
        log "rsync -rt --progress --exclude=copycomplete.txt --exclude='Undetermined*' ${RUNDIR} ${TARGET_SERVER}:${TARGET_DIR}"
        rsync -rt --progress --exclude=copycomplete.txt --exclude='Undetermined*' ${RUNDIR} ${TARGET_SERVER}:${TARGET_DIR}
        log "scp ${RUNDIR}/copycomplete.txt ${TARGET_SERVER}:${TARGET_DIR}/${RUN}/"
        scp ${RUNDIR}/copycomplete.txt ${TARGET_SERVER}:${TARGET_DIR}/${RUN}/
        log "ssh ${TARGET_SERVER} 'rm ${TARGET_DIR}/${RUN}/delivery.txt'"
        ssh ${TARGET_SERVER} "rm -f ${TARGET_DIR}/${RUN}/delivery.txt"
        continue
    fi

    log "${RUN} copied"
done
