#!/bin/bash
#   usage: demux-2500.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $OUT_DIR

set -eu -o pipefail

shopt -s expand_aliases

VERSION=5.11.1

##########
# PARAMS #
##########

IN_DIR=${1?'please provide a run dir'}
OUT_DIR=${2?'please provide a demux dir'}
ENVIRONMENT=${3?'please provide an environment'}
LANE=${4:-1}
EMAIL=clinical-demux@scilifelab.se

RUN=$(basename ${IN_DIR})
RUN_DIR=$(dirname ${IN_DIR})
PROJECTLOG=${OUT_DIR}/${RUN}/projectlog.$(date +"%Y%m%d%H%M%S").log
SCRIPT_DIR=/home/proj/${ENVIRONMENT}/bin/git/demultiplexing/scripts/2500/

if [[ ${ENVIRONMENT} == 'production' ]]; then
    useprod
    SLURM_ACCOUNT=production
elif [[ ${ENVIRONMENT} == 'stage' ]]; then
    usestage
    SLURM_ACCOUNT=development
fi  



#############
# FUNCTIONS #
#############

log() {
    local NOW=$(date +"%Y%m%d%H%M%S")
    # the weird sed command converts control chars to the string representation
    echo "[$NOW] $@"
    echo "[$NOW] $@" | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g" >> ${PROJECTLOG}
}

failed() {
    cat ${PROJECTLOG} | mail -s "ERROR demux $(hostname):${RUN}" ${EMAIL}
}
trap failed ERR

###########
# PREMAIN #
###########

# transform SampleSheet from Mac to Unix
if [[ ! -e ${IN_DIR}/SampleSheet.ori ]]; then
    cp ${IN_DIR}/SampleSheet.csv ${IN_DIR}/SampleSheet.ori
    if grep -qs $'\r' ${IN_DIR}/SampleSheet.csv; then
        sed -i 's/
/\n/g' ${IN_DIR}/SampleSheet.csv
    fi
    sed -i '/^$/d' ${IN_DIR}/SampleSheet.csv # remove empty lines
fi

########
# MAIN #
########

# init
mkdir -p ${OUT_DIR}/${RUN}
log "${PROJECTLOG} created by $0 $VERSION"
date > ${IN_DIR}/demuxstarted.txt
cp ${IN_DIR}/SampleSheet.csv ${IN_DIR}/Data/Intensities/BaseCalls/SampleSheet.csv

# here we go!
log "Setup correct, starts demuxing . . ."

echo "get basemask ${IN_DIR}"
BASEMASK=$(demux basemask create --application wes --lane ${LANE} ${IN_DIR})
UNALIGNED_DIR=Unaligned-${BASEMASK//,}

# DEMUX !
JOB_TITLE=Demux_${RUN}
log "sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${PROJECTLOG} ${SCRIPT_DIR}/demux-2500.sh ${IN_DIR} ${OUT_DIR}/${RUN} ${BASEMASK} ${UNALIGNED_DIR}"
RES=$(sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${PROJECTLOG} ${SCRIPT_DIR}/demux-2500.sh ${IN_DIR} ${OUT_DIR}/${RUN} ${BASEMASK} ${UNALIGNED_DIR})

log "bcl2fastq finished!"

# Add samplesheet to unaligned folder
cp ${IN_DIR}/SampleSheet.csv ${OUT_DIR}/${RUN}/${UNALIGNED_DIR}/

# Restructure the output dir!
FC=${RUN##*_}
FC=${FC:1}
shopt -s nullglob
for PROJECT_DIR in ${OUT_DIR}/${RUN}/${UNALIGNED_DIR}/*; do
    if [[ ! -d ${PROJECT_DIR} ]]; then continue; fi

    PROJECT=$(basename ${PROJECT_DIR})
    if [[ ${PROJECT} == 'Stats' ]]; then continue; fi
    if [[ ${PROJECT} == 'Reports' ]]; then continue; fi
    if [[ ${PROJECT} =~ Project_* ]]; then continue; fi
    if [[ ${PROJECT} == 'indexcheck' ]]; then
        mv ${PROJECT_DIR} ${OUT_DIR}/${RUN}/${UNALIGNED_DIR}/Project_${PROJECT}
        continue
    fi

    for SAMPLE_DIR in ${PROJECT_DIR}/*; do
        for FASTQ_FILE in ${SAMPLE_DIR}/*; do
            FASTQ=$(basename ${FASTQ_FILE})
            SAMPLE=$(basename ${SAMPLE_DIR})
            LANE_READ_PART=${FASTQ#*_*_}
            INDEX="NNNNNNNN-NNNNNNNN"
            log "mv ${FASTQ_FILE} ${SAMPLE_DIR}/${SAMPLE}_${INDEX}_${LANE_READ_PART}"
            mv ${FASTQ_FILE} ${SAMPLE_DIR}/${SAMPLE}_${INDEX}_${LANE_READ_PART}
        done

        SAMPLE=$(basename ${SAMPLE_DIR})
        log "mv ${SAMPLE_DIR} ${PROJECT_DIR}/Sample_${SAMPLE}"
        mv ${SAMPLE_DIR} ${PROJECT_DIR}/Sample_${SAMPLE}
    done

    log "mv ${PROJECT_DIR} ${OUT_DIR}/${RUN}/${UNALIGNED_DIR}/Project_${PROJECT}"
    mv ${PROJECT_DIR} ${OUT_DIR}/${RUN}/${UNALIGNED_DIR}/Project_${PROJECT}
done

# Add stats
log "cgstats add --machine 2500 --unaligned ${UNALIGNED_DIR} ${OUT_DIR}/${RUN}/"
cgstats add --machine 2500 --unaligned ${UNALIGNED_DIR} ${OUT_DIR}/${RUN}/ &>> ${PROJECTLOG}

# create stats files
FC=$(echo ${RUN} | awk 'BEGIN {FS="/"} {split($(NF),arr,"_");print substr(arr[4],2,length(arr[4]))}')
PROJs=$(ls ${OUT_DIR}/${RUN}/${UNALIGNED_DIR}/ | grep Proj)
for PROJ in ${PROJs[@]}; do
    prj=$(echo ${PROJ} | sed 's/Project_//')
    log "cgstats select --project ${prj} ${FC} &> ${OUT_DIR}/${RUN}/stats-${prj}-${FC}.txt"
    cgstats select --project ${prj} ${FC} &> ${OUT_DIR}/${RUN}/stats-${prj}-${FC}.txt
done

log "rm -f ${OUT_DIR}/${RUN}/copycomplete.txt"
rm -f ${OUT_DIR}/${RUN}/copycomplete.txt

log "date > ${OUT_DIR}/${RUN}/demuxcomplete.txt"
date > ${OUT_DIR}/${RUN}/demuxcomplete.txt

