#!/bin/bash

set -eu
shopt -s nullglob

VERSION=3.4.3

########
# VARS #
########

INDIR=${1-/home/clinical/DEMUX/}
TARGET_SERVER=${2-hasta.scilifelab.se}
TARGET_DIR=${3-/home/proj/production/demultiplexed-runs/}
TARGET_SERVER_HASTA=rastapopoulos.scilifelab.se
TARGET_DIR_HASTA=/mnt/hds/proj/bioinfo/DEMUX/
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
        log "rsync -a ${RUNDIR} ${TARGET_SERVER}:${TARGET_DIR}"
        rsync -rvt --progress --exclude=copycomplete.txt ${RUNDIR} ${TARGET_SERVER}:${TARGET_DIR}
        log "scp ${RUNDIR}/copycomplete.txt ${TARGET_SERVER}:${TARGET_DIR}/${RUN}/"
        scp ${RUNDIR}/copycomplete.txt ${TARGET_SERVER}:${TARGET_DIR}/${RUN}/
        log "ssh ${TARGET_SERVER} 'rm ${TARGET_DIR}/${RUN}/delivery.txt'"
        ssh ${TARGET_SERVER} "rm -f ${TARGET_DIR}/${RUN}/delivery.txt"
        if [[ -n ${EMAILS} ]]; then
            log "column -t ${RUNDIR}/stats-* | mail -s 'DEMUX ${RUN} delivered to ${TARGET_SERVER}' ${EMAILS}"
            column -t ${RUNDIR}/stats-* | mail -s "DEMUX ${RUN} delivered to ${TARGET_SERVER}" ${EMAILS}
        fi
        rsync -rvt --progress --exclude=copycomplete.txt ${RUNDIR} ${TARGET_SERVER_HASTA}:${TARGET_DIR_HASTA}
        log "scp ${RUNDIR}/copycomplete.txt ${TARGET_SERVER_HASTA}:${TARGET_DIR_HASTA}/${RUN}/"
        scp ${RUNDIR}/copycomplete.txt ${TARGET_SERVER_HASTA}:${TARGET_DIR_HASTA}/${RUN}/
        if [[ -n ${EMAILS} ]]; then
            log "column -t ${RUNDIR}/stats-* | mail -s 'DEMUX ${RUN} delivered to ${TARGET_SERVER_HASTA}' ${EMAILS}"
            column -t ${RUNDIR}/stats-* | mail -s "DEMUX ${RUN} delivered to ${TARGET_SERVER_HASTA}" ${EMAILS}
        fi
        continue
    fi

    log "${RUN} copied"
done
