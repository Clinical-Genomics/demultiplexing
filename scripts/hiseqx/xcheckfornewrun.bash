#!/bin/bash

set -eu -o pipefail
source "${HOME}/.bashrc"
shopt -s expand_aliases

########
# VARS #
########

SCRIPT_DIR="$(dirname "$(readlink -nm "$0")")"
RUNS_DIR=${1?please provide a runs dir} #/home/proj/${ENVIRONMENT-stage}/flowcells/hiseqx/
DEMUXES_DIR=${2?please provide a demuxes dir} #/home/proj/${ENVIRONMENT-stage}/demultiplexed-runs/
EMAIL=${3-clinical-demux@scilifelab.se}

#############
# FUNCTIONS #
#############

function join { local IFS="$1"; shift; echo "$*"; }

log() {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] $@"
}

failed() {
    echo "ERROR starting X demultiplexing: ${RUN} by $(caller)" | mail -s "ERROR starting X demultiplexing" $EMAIL
}
trap failed ERR

########
# MAIN #
########

for RUN in "${RUNS_DIR}"/*; do
    RUN="$(basename "${RUN}/")"
    FC=$( echo "${RUN}" | awk 'BEGIN {FS="_"} {print substr($4,2,length($4))}')

    if [[ -f "${RUNS_DIR}/${RUN}/RTAComplete.txt" ]]; then
        if [ ! -f ${RUNS_DIR}/${RUN}/demuxstarted.txt ]; then

            # process FCs serially
            FCS=( $(squeue --format=%j | grep Xdem | grep -v ${FC} | cut -d- -f 3 | sort | uniq) )
            if [[ ${#FCS[@]} -gt 0 ]]; then
                RUNNING_FCS=$(join , "${FCS[@]}")
                log "${RUN} ${RUNNING_FCS} are demuxing - Postpone demux!"
                continue
            fi

            log "${RUN} starting demultiplexing"
            date +'%Y%m%d%H%M%S' > ${RUNS_DIR}/${RUN}/demuxstarted.txt

            mkdir -p ${DEMUXES_DIR}/${RUN}/
            PROJECTLOG=${DEMUXES_DIR}/${RUN}/projectlog.$(date +'%Y%m%d%H%M%S').log
            ${SCRIPT_DIR}/xdemuxtiles.bash ${RUNS_DIR}/${RUN} &>> ${PROJECTLOG}
            rm -f ${DEMUXES_DIR}/${RUN}/copycomplete.txt
            rm -f ${DEMUXES_DIR}/${RUN}/delivery.txt
        else
            log "${RUN} is finished and demultiplexing has already started"
        fi
    else
        log "${RUN} is not finished yet"
    fi
done
