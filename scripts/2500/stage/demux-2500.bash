#!/bin/bash
#   usage: demux-2500.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $OUT_DIR

set -eu -o pipefail

shopt -s expand_aliases
source /home/barry.stokman/development/demultiplexing/scripts/2500/stage/demux.functions

VERSION=5.4.2

##########
# PARAMS #
##########

IN_DIR=${1?'please provide a run dir'}
OUT_DIR=${2?'please provide a demux dir'}
EMAIL=barry.stokman@scilifelab.se

RUN=$(basename ${IN_DIR})
RUN_DIR=$(dirname ${IN_DIR})
PROJECTLOG=${OUT_DIR}/${RUN}/projectlog.$(date +"%Y%m%d%H%M%S").txt

SCRIPT_DIR=/home/barry.stokman/development/demultiplexing/scripts/2500/stage/  # use this when developing in a conda env
#SCRIPT_DIR=/home/proj/${ENVIRONMENT}/bin/git/demultiplexing/scripts/novaseq/        # use this when testing on stage

SLURM_ACCOUNT=development
if [[ ${ENVIRONMENT} == 'production' ]]; then
    SLURM_ACCOUNT=production
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
cp ${IN_DIR}/SampleSheet.csv ${OUT_DIR}/${RUN}/
cp ${IN_DIR}/SampleSheet.csv ${IN_DIR}/Data/Intensities/BaseCalls/SampleSheet.csv

# here we go!
log "Setup correct, starts demuxing . . ."

echo $(get_basemask ${IN_DIR})
BASEMASK=$(get_basemask ${IN_DIR})
UNALIGNED_DIR=Unaligned-${BASEMASK//,}

# DEMUX !
#log "/usr/local/bin/configureBclToFastq.pl --force --sample-sheet ${IN_DIR}/Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${BASEMASK} --fastq-cluster-count 0 --input-dir ${IN_DIR}/Data/Intensities/BaseCalls --output-dir ${OUT_DIR}/${RUN}/${UNALIGNED_DIR}"
## the sed command is there to remove the color codes out of the demux output and create a pretty log file
#/usr/local/bin/configureBclToFastq.pl --force --sample-sheet ${IN_DIR}/Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${BASEMASK} --fastq-cluster-count 0 --input-dir ${IN_DIR}/Data/Intensities/BaseCalls --output-dir ${OUT_DIR}/${RUN}/${UNALIGNED_DIR} 2>&1 | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g" >> ${PROJECTLOG}

JOB_TITLE=Demux_${RUN}
log "sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${PROJECTLOG} ${SCRIPT_DIR}/demux-2500.sh ${IN_DIR} ${OUT_DIR}/${RUN} ${BASEMASK} ${UNALIGNED_DIR}"
RES=$(sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${PROJECTLOG} ${SCRIPT_DIR}/demux-2500.sh ${IN_DIR} ${OUT_DIR}/${RUN} ${BASEMASK} ${UNALIGNED_DIR})

cd ${OUT_DIR}/${RUN}/${UNALIGNED_DIR}
#nohup make -j 8 > nohup.$(date +"%Y%m%d%H%M%S").out 2>&1  #TODO: find out wht this does

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