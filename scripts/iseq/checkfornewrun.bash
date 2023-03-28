#!/bin/bash

set -u

shopt -s nullglob
shopt -s expand_aliases
source "${HOME}/.aliases"

########
# VARS #
########

IN_DIR=${1?'please provide the runs dir'}
DEMUXES_DIR=${2?'please provide the demuxes dir'}
SCRIPT_DIR=$(dirname "$(readlink -nm "$0")")
EMAIL=clinical-demux@scilifelab.se

INDIR=${1?'please provide a run dir'}
DEMUXDIR=${2?'please provide a demux dir'}

CONDA_BASE="/home/proj/${ENVIRONMENT}/bin/miniconda3"
CONDA_EXE="${CONDA_BASE}/bin/conda"
CONDA_ENV_BASE="${CONDA_BASE}/envs"
CONDA_ENV_BIN_BASE="${CONDA_ENV}/bin"
CONDA_ENV="S_demux"

HOSTNAME=$(hostname)
DEMUX_CONFIG="/home/proj/${ENVIRONMENT}/servers/config/${HOSTNAME}/demux-stage.yaml"
if [[ ${ENVIRONMENT} == 'production' ]]; then
    CONDA_ENV="P_demux"
    DEMUX_CONFIG="/home/proj/${ENVIRONMENT}/servers/config/${HOSTNAME}/demux.yaml"
fi



#############
# FUNCTIONS #
#############

log () {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] $*"
}

failed() {
    cat "${PROJECTLOG}" | mail -s "ERROR starting iseq ${FC} on $(hostname)" $EMAIL
}
trap failed ERR

########
# MAIN #
########

if pgrep bcl2fastq; then
    log "an instance of bcl2fastq is already running -- skipping"
    exit 0
fi

for RUN_DIR in "${IN_DIR}"/*; do
    if [[ ! -d ${RUN_DIR} ]]; then
        continue
    fi

    RUN=$(basename "${RUN_DIR}")
    FC=${RUN##*_}
    FC=${FC:1}
    PROJECTLOG=${DEMUXES_DIR}/${RUN}/projectlog.$(date +'%Y%m%d%H%M%S').log

    if [[ -f ${RUN_DIR}/RTAComplete.txt ]]; then
        if [[ ! -f ${RUN_DIR}/demuxstarted.txt ]]; then
            log "date +'%Y%m%d%H%M%S' > ${RUN_DIR}/demuxstarted.txt"
            date +'%Y%m%d%H%M%S' > "${RUN_DIR}/demuxstarted.txt"

            if [[ ! -e ${RUN_DIR}/SampleSheet.csv ]]; then
                log "${CONDA_EXE} run --name ${CONDA_ENV} ${CONDA_ENV_BIN_BASE}/demux sheet fetch --application iseq --pad --longest ${FC} > ${RUN_DIR}/SampleSheet.csv"
                $CONDA_EXE run --name $CONDA_ENV $CONDA_ENV_BIN_BASE/demux -c "${DEMUX_CONFIG}" sheet fetch --application iseq --pad --longest "${FC}" > "${RUN_DIR}/SampleSheet.csv"
            fi

            log "mkdir -p ${DEMUXES_DIR}/${RUN}/"
            mkdir -p "${DEMUXES_DIR}/${RUN}/"

            log "bash ${SCRIPT_DIR}/demux-iseq.bash ${RUN_DIR} ${DEMUXES_DIR} &>> ${PROJECTLOG}"
            if bash "${SCRIPT_DIR}/demux-iseq.bash" "${RUN_DIR}" "${DEMUXES_DIR}" &>> "${PROJECTLOG}"; then
                log "rm -f ${DEMUXES_DIR}/${RUN}/copycomplete.txt"
                rm -f "${DEMUXES_DIR}/${RUN}/copycomplete.txt"
                log "date +'%Y%m%d%H%M%S' > ${DEMUXES_DIR}/${RUN}/demuxcomplete.txt"
                date +'%Y%m%d%H%M%S' > "${DEMUXES_DIR}/${RUN}/demuxcomplete.txt"
            fi
        else
            log "${RUN} is finished and demultiplexing has already started"
        fi
    else
        log "${RUN} is not finished yet"
    fi
done
