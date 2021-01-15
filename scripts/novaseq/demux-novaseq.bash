#!/usr/bin/env bash

set -eu

shopt -s expand_aliases
#source $HOME/.bashrc
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
LOG_DIR="${OUT_DIR}/LOG"
SCRIPT_DIR=/home/proj/${ENVIRONMENT}/bin/git/demultiplexing/scripts/novaseq/
#EMAIL=clinical-demux@scilifelab.se
EMAIL=barry.stokman@scilifelab.se

SLURM_ACCOUNT=development
if [[ ${ENVIRONMENT} == 'P_main' ]]; then
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
mkdir -p ${LOG_DIR}

# Here we go!
log "Starting NovaSeq demultiplexing"
# Send a mail that demultiplexing has started
cat ${PROJECTLOG} | mail -s "Starting demultiplexing of novaseq flowcell ${FC} on $(hostname)" $EMAIL

BASEMASK=$(demux basemask create --application nova ${IN_DIR})
UNALIGNED_DIR=Unaligned-${BASEMASK//,}

# DEMUX !
JOB_TITLE=Demux_${RUN}
log "sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${LOG_DIR}/${JOB_TITLE}-%j.log -e ${LOG_DIR}/${JOB_TITLE}-%j.err ${SCRIPT_DIR}/demux-novaseq.batch ${IN_DIR} ${OUT_DIR} ${BASEMASK} ${UNALIGNED_DIR}"
RES=$(sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${LOG_DIR}/${JOB_TITLE}-%j.log -e ${LOG_DIR}/${JOB_TITLE}-%j.err ${SCRIPT_DIR}/demux-novaseq.batch ${IN_DIR} ${OUT_DIR} ${BASEMASK} ${UNALIGNED_DIR})

log "bcl2fastq finished!"

#add samplesheet to unaligned folder
cp ${IN_DIR}/SampleSheet.csv ${OUT_DIR}/${UNALIGNED_DIR}/

#Restructure the output dir!
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

#Add stats to cgstats database
log "cgstats add --machine novaseq --unaligned ${UNALIGNED_DIR} ${OUT_DIR}"
cgstats add --machine novaseq --unaligned ${UNALIGNED_DIR} ${OUT_DIR}

PROJECTS=$(ls ${OUT_DIR}/${UNALIGNED_DIR}/ | grep Project_)
for PROJECT_DIR in ${PROJECTS[@]}; do
    PROJECT=${PROJECT_DIR##*_}
    log "cgstats select --project ${PROJECT} ${FC} &> ${OUT_DIR}/stats-${PROJECT}-${FC}.txt"
    cgstats select --project ${PROJECT} ${FC} &> ${OUT_DIR}/stats-${PROJECT}-${FC}.txt
done
