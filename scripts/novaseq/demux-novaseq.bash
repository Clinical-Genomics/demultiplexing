#!/usr/bin/env bash

set -eu

ulimit -n 4096

##########
# PARAMS #
##########

IN_DIR=${1?'please provide a run dir'}
DEMUXES_DIR=${2?'please provide the demuxes dir'}
FC=${3?'fc_id needed'}
PROJECTLOG=${4?'projectlog needed'}

RUN=$(basename ${IN_DIR})
OUT_DIR=${DEMUXES_DIR}/${RUN}
SCRIPT_DIR=/home/proj/${ENVIRONMENT}/bin/git/demultiplexing/scripts/novaseq/
EMAIL=clinical-demux@scilifelab.se

SLURM_ACCOUNT=development
if [[ ${ENVIRONMENT} == 'production' ]]; then
    SLURM_ACCOUNT=production
fi

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

# Here we go!
log "Starting NovaSeq demultiplexing"
# Send a mail that demultiplexing has started
cat ${PROJECTLOG} | mail -s "Starting demultiplexing of novaseq flowcell ${FC} on $(hostname)" $EMAIL


UNALIGNED_DIR='Unaligned'

# DEMUX !
JOB_TITLE=Demux_${RUN}
log "sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${PROJECTLOG} ${SCRIPT_DIR}/demux-novaseq.sh ${IN_DIR} ${OUT_DIR} ${UNALIGNED_DIR}"
RES=$(sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${PROJECTLOG} ${SCRIPT_DIR}/demux-novaseq.sh ${IN_DIR} ${OUT_DIR} ${UNALIGNED_DIR})

log "bcl2fastq finished!"

# Restructure the output dir!
FC=${RUN##*_}
FC=${FC:1}
shopt -s nullglob
for PROJECT_DIR in ${OUT_DIR}/${UNALIGNED_DIR}/*; do
    if [[ ! -d ${PROJECT_DIR} ]]; then continue; fi

    PROJECT=$(basename ${PROJECT_DIR})
    if [[ ${PROJECT} == 'Stats' ]]; then continue; fi
    if [[ ${PROJECT} == 'Reports' ]]; then continue; fi
    if [[ ${PROJECT} =~ Project_* ]]; then continue; fi
    if [[ ${PROJECT} == 'indexcheck' ]]; then
        mv ${PROJECT_DIR} ${OUT_DIR}/${UNALIGNED_DIR}/Project_${PROJECT}
        continue
    fi

    for SAMPLE_DIR in ${PROJECT_DIR}/*; do
        for FASTQ_FILE in ${SAMPLE_DIR}/*; do
            FASTQ=$(basename ${FASTQ_FILE})
            log "mv ${FASTQ_FILE} ${SAMPLE_DIR}/${FC}_${FASTQ}"
            mv ${FASTQ_FILE} ${SAMPLE_DIR}/${FC}_${FASTQ}
        done

        SAMPLE=$(basename ${SAMPLE_DIR})
        log "mv ${SAMPLE_DIR} ${PROJECT_DIR}/Sample_${SAMPLE}"
        mv ${SAMPLE_DIR} ${PROJECT_DIR}/Sample_${SAMPLE}
    done

    log "mv ${PROJECT_DIR} ${OUT_DIR}/${UNALIGNED_DIR}/Project_${PROJECT}"
    mv ${PROJECT_DIR} ${OUT_DIR}/${UNALIGNED_DIR}/Project_${PROJECT}
done


# Create a summary of the bcl2fastq indexcheck report
demux indexreport summary \
  --index-report-path "$OUT_DIR/$UNALIGNED_DIR/Reports/html/$FC/all/all/all/laneBarcode.html" \
  --out-dir "$OUT_DIR" \
  --cluster-counts 1000000 \
  --run-parameters-path "$IN_DIR/RunParameters.xml"
