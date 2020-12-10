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
EMAIL=clinical-demux@scilifelab.se

#############
# FUNCTIONS #
#############

log () {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo ["${NOW}"] "$@"
}

failed() {
    cat "${PROJECTLOG}" | mail -s "ERROR starting novaseq ${FC} on $(hostname)" $EMAIL
}
trap failed ERR

########
# MAIN #
########

if pgrep bcl2fastq; then
    log "an instance of bcl2fastq is already running -- skipping"
    exit 0
fi

for RUN_DIR in ${IN_DIR}/*; do
    if [[ ! -d ${RUN_DIR} ]]; then
        continue
    fi

    RUN=$(basename ${RUN_DIR})
    FC=${RUN##*_}
    FC=${FC:1}
    PROJECTLOG=${DEMUXES_DIR}/${RUN}/projectlog.$(date +'%Y%m%d%H%M%S').log

    if [[ -f ${RUN_DIR}/RTAComplete.txt ]]; then
        if [[ ! -f ${RUN_DIR}/demuxstarted.txt ]]; then

            # start with a clean slate: remove empty sample sheets before continuing
            if [[ ! -s ${RUN_DIR}/SampleSheet.csv  ]]; then
                rm ${RUN_DIR}/SampleSheet.csv
            fi

            if [[ ! -e ${RUN_DIR}/SampleSheet.csv ]]; then
                log "demux sheet fetch --application nova --pad --longest ${FC} > ${RUN_DIR}/SampleSheet.csv"
                demux sheet fetch --application nova --pad --longest "${FC}" > "${RUN_DIR}"/SampleSheet.csv
            fi

            # exit if samplesheet is still empty after running demux sheet fetch
            if [[ ! -s ${RUN_DIR}/SampleSheet.csv ]]; then
                echo "Sample sheet empty! Exiting!" 1>&2
                continue
            fi

            log "mkdir -p ${DEMUXES_DIR}/${RUN}/"
            mkdir -p ${DEMUXES_DIR}/${RUN}/

            log "date +'%Y%m%d%H%M%S' > ${RUN_DIR}/demuxstarted.txt"
            date +'%Y%m%d%H%M%S' > ${RUN_DIR}/demuxstarted.txt

            log "bash ${SCRIPT_DIR}/demux-novaseq.bash ${RUN_DIR} ${DEMUXES_DIR} &>> ${PROJECTLOG}"
            bash "${SCRIPT_DIR}"/demux-novaseq.bash "${RUN_DIR}" "${DEMUXES_DIR}" &>> "${PROJECTLOG}"

            if [[ $? == 0 ]]; then
                log "rm -f ${DEMUXES_DIR}/${RUN}/copycomplete.txt"
                rm -f ${DEMUXES_DIR}/${RUN}/copycomplete.txt
                log "date +'%Y%m%d%H%M%S' > ${DEMUXES_DIR}/${RUN}/demuxcomplete.txt"
                date +'%Y%m%d%H%M%S' > "${DEMUXES_DIR}"/"${RUN}"/demuxcomplete.txt
            fi

            # This is an easy way to avoid running multiple demuxes at the same time
            break
        else
            log "${RUN} is finished and demultiplexing has already started"
        fi
    else
        log "${RUN} is not finished yet"
    fi
done
