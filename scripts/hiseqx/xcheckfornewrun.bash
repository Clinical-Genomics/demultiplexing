#!/bin/bash

shopt -s expand_aliases
source ~/.bashrc

set -e
set -u

########
# VARS #
########

SCRIPT_DIR=$(dirname $(readlink -nm $0))
RAWBASE=/mnt/hds2/proj/bioinfo/Runs/
DEMUX_DIR=/mnt/hds/proj/bioinfo/DEMUX/
EMAIL=kenny.billiau@scilifelab.se

#############
# FUNCTIONS #
#############

function join { local IFS="$1"; shift; echo "$*"; }

log() {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo [${NOW}] $@
}

failed() {
    echo "ERROR starting X demultiplexing" | mail -s "ERROR starting X demultiplexing" $EMAIL
}
trap failed ERR

########
# MAIN #
########

for RUN in ${RAWBASE}/*; do
    RUN=$(basename ${RUN}/)
    FC=$( echo ${RUN} | awk 'BEGIN {FS="_"} {print substr($4,2,length($4))}')

    if [ -f ${RAWBASE}/${RUN}/RTAComplete.txt ]; then
        if [ ! -f ${RAWBASE}/${RUN}/demuxstarted.txt ]; then

            # process FCs serially
            FCS=( $(squeue --format=%j | grep Xdem | grep -v ${FC} | cut -d- -f 3 | sort | uniq) )
            if [[ ${#FCS[@]} > 0 ]]; then
                RUNNING_FCS=$(join , ${FCS[@]})
                log "${RUN} ${RUNNING_FCS} are demuxing - Postpone demux!"
                continue
            fi

            log "${RUN} starting demultiplexing"
            date +'%Y%m%d%H%M%S' > ${RAWBASE}/${RUN}/demuxstarted.txt

            mkdir -p ${DEMUX_DIR}/${RUN}/
            PROJECTLOG=${DEMUX_DIR}/${RUN}/projectlog.$(date +'%Y%m%d%H%M%S').log
            ${SCRIPT_DIR}/xdemuxtiles.bash ${RAWBASE}/${RUN} &>> ${PROJECTLOG}
        else
            log "${RUN} is finished and demultiplexing has already started"
        fi
    else
        log "${RUN} is not finished yet"
    fi
done
