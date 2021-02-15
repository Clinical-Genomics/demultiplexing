#!/usr/bin/env bash

set -eu

shopt -s expand_aliases
source $HOME/.bashrc
ulimit -n 4096

##########
# PARAMS #
##########

IN_DIR=${1?'please provide a run dir'}
DEMUXES_DIR=${2?'please provide the demuxes dir'}

RUN=$(basename ${IN_DIR})
OUT_DIR=${DEMUXES_DIR}/${RUN}
EMAIL=clinical-demux@scilifelab.se

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
demux --version
${BCL2FASTQ_BIN} --version

# Here we go!
log "Starting NovaSeq demultiplexing"
# Send a mail that demultiplexing has started
cat ${PROJECTLOG} | mail -s "Starting demultiplexing of novaseq flowcell ${FC} on $(hostname)" $EMAIL

BASEMASK=$(demux basemask create --application nova ${IN_DIR})
UNALIGNED_DIR=Unaligned-${BASEMASK//,}

# DEMUX !
log "${BCL2FASTQ_BIN} --loading-threads 3 --processing-threads 15 --writing-threads 3 --runfolder-dir ${IN_DIR} --output-dir ${OUT_DIR}/${UNALIGNED_DIR} --use-bases-mask ${BASEMASK} --sample-sheet ${IN_DIR}/SampleSheet.csv --barcode-mismatches 1"
${BCL2FASTQ_BIN} --loading-threads 3 --processing-threads 15 --writing-threads 3 --runfolder-dir ${IN_DIR} --output-dir ${OUT_DIR}/${UNALIGNED_DIR} --use-bases-mask ${BASEMASK} --sample-sheet ${IN_DIR}/SampleSheet.csv --barcode-mismatches 1

# add samplesheet to unaligned folder
cp ${IN_DIR}/SampleSheet.csv ${OUT_DIR}/${UNALIGNED_DIR}/

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

# Need to add stats code here :)
log "cgstats add --machine novaseq --unaligned ${UNALIGNED_DIR} ${OUT_DIR}"
cgstats add --machine novaseq --unaligned ${UNALIGNED_DIR} ${OUT_DIR}

PROJECTS=$(ls ${OUT_DIR}/${UNALIGNED_DIR}/ | grep Project_)
for PROJECT_DIR in ${PROJECTS[@]}; do
    PROJECT=${PROJECT_DIR##*_}
    log "cgstats select --project ${PROJECT} ${FC} &> ${OUT_DIR}/stats-${PROJECT}-${FC}.txt"
    cgstats select --project ${PROJECT} ${FC} &> ${OUT_DIR}/stats-${PROJECT}-${FC}.txt
done

# Create a summary of the bcl2fastq indexcheck report
demux indexreport summary \
  --index-report-path "${OUT_DIR}/${UNALIGNED_DIR}/Reports/html/${FC}/all/all/all/laneBarcode.html" \
  --out-dir "$OUT_DIR" \
  --cluster-counts 1000000 \
  --run-parameters-path "$IN_DIR/RunParameters.xml"


