#!/bin/bash

set -eu
shopt -s nullglob

VERSION=3.4.3

########
# VARS #
########

INDIR=${1-/home/clinical/DEMUX/}
TARGET_SERVER=${2-rastapopoulos.scilifelab.se}
TARGET_DIR=${3-/mnt/hds/proj/bioinfo/DEMUX/}
EMAILS=${4-}

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
        log "rsync -a ${RUNDIR} ${TARGET_SERVER}:${TARGET_DIR}"
        rsync -a --exclude=copycomplete.txt ${RUNDIR} ${TARGET_SERVER}:${TARGET_DIR}
        log "rsync -a --checksum ${RUNDIR} ${TARGET_SERVER}:${TARGET_DIR}"
        rsync -a --checksum --exclude=copycomplete.txt ${RUNDIR} ${TARGET_SERVER}:${TARGET_DIR}
        log "scp ${RUNDIR}/copycomplete.txt ${TARGET_SERVER}:${TARGET_DIR}/${RUN}/"
        scp ${RUNDIR}/copycomplete.txt ${TARGET_SERVER}:${TARGET_DIR}/${RUN}/
        if [[ -n ${EMAILS} ]]; then
            log "column -t ${RUNDIR}/stats-* | mail -s 'DEMUX ${RUN} finished' ${EMAILS}"
            column -t ${RUNDIR}/stats-* | mail -s "DEMUX ${RUN} finished" ${EMAILS}
        fi
        continue
    fi

    log "${RUN} copied"
done