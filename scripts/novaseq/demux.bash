#!/usr/bin/env bash

set -eu -o pipefail

shopt -s expand_aliases
source $HOME/.bashrc
source $HOME/SCRIPTS/demux.functions

VERSION=4.23.0

##########
# PARAMS #
##########

IN_DIR=${1?'please provide a run dir'}
DEMUX_DIR=${2?'please provide a demux dir'}

RUN=$(basename ${IN_DIR})
RUN_DIR=$(dirname ${IN_DIR})
OUT_DIR=${DEMUX_DIR}/${RUN}

BCL2FASTQ_BIN=/usr/local/bcl2fastq2/bin/bcl2fastq

#############
# FUNCTIONS #
#############

log() {
    local NOW=$(date +"%Y%m%d%H%M%S")
    echo "[$NOW] $@"
}

########
# MAIN #
########

# init
mkdir -p ${OUT_DIR}

# log the version
${BCL2FASTQ_BIN} --version

# Here we go!
log "Here we go!"

BASEMASK=Y151,I8,I10,Y151
UNALIGNED_DIR=Unaligned-${BASEMASK}

# DEMUX !
log "${BCL2FASTQ_BIN} --loading-threads 3 --processing-threads 12 --writing-threads 3 --output-dir ${OUT_DIR}/${UNALIGNED_DIR} --use-bases-mask ${BASEMASK} --sample-sheet ${IN_DIR}/SampleSheet.csv"
#${BCL2FASTQ_BIN} --loading-threads 3 --processing-threads 12 --writing-threads 3 --output-dir ${OUT_DIR}/${UNALIGNED_DIR} --use-bases-mask ${BASEMASK} --sample-sheet ${INDIR}/SampleSheet.csv

# Need to add stats code here :)
