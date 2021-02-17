#!/bin/bash
#   usage: demux-2500.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $DEMUX_DIR

set -eu -o pipefail

shopt -s expand_aliases
source /home/barry.stokman/development/demultiplexing/scripts/2500/stage/demux.functions

VERSION=5.4.2

##########
# PARAMS #
##########

BASE=${1?'please provide a run dir'}
DEMUX_DIR=${2?'please provide a demux dir'}
EMAIL=barry.stokman@scilifelab.se

RUN=$(basename ${BASE})
RUN_DIR=$(dirname ${BASE})
PROJECTLOG=${DEMUX_DIR}/${RUN}/projectlog.$(date +"%Y%m%d%H%M%S").txt

SCRIPT_DIR=/home/proj/${CONDA_DEFAULT_ENV}/bin/git/demultiplexing/scripts/novaseq/  # use this when developing in a conda env
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
if [[ ! -e ${BASE}/SampleSheet.ori ]]; then
    cp ${BASE}/SampleSheet.csv ${BASE}/SampleSheet.ori
    if grep -qs $'\r' ${BASE}/SampleSheet.csv; then
        sed -i 's/
/\n/g' ${BASE}/SampleSheet.csv
    fi
    sed -i '/^$/d' ${BASE}/SampleSheet.csv # remove empty lines
fi

########
# MAIN #
########

# init
mkdir -p ${DEMUX_DIR}/${RUN}
log "${PROJECTLOG} created by $0 $VERSION"
date > ${BASE}/demuxstarted.txt
cp ${BASE}/SampleSheet.csv ${DEMUX_DIR}/${RUN}/
cp ${BASE}/SampleSheet.csv ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv

# here we go!
log "Setup correct, starts demuxing . . ."

echo $(get_basemask ${BASE})
BASEMASK=$(get_basemask ${BASE})
UNALDIR=Unaligned-${BASEMASK//,}

# DEMUX !
#log "/usr/local/bin/configureBclToFastq.pl --force --sample-sheet ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${BASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}/Data/Intensities/BaseCalls --output-dir ${DEMUX_DIR}/${RUN}/${UNALDIR}"
## the sed command is there to remove the color codes out of the demux output and create a pretty log file
#/usr/local/bin/configureBclToFastq.pl --force --sample-sheet ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${BASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}/Data/Intensities/BaseCalls --output-dir ${DEMUX_DIR}/${RUN}/${UNALDIR} 2>&1 | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g" >> ${PROJECTLOG}

JOB_TITLE=Demux_${RUN}
log "sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${PROJECTLOG} ${SCRIPT_DIR}/demux-2500.sh ${IN_DIR} ${OUT_DIR} ${BASEMASK} ${UNALIGNED_DIR}"
RES=$(sbatch --wait -A ${SLURM_ACCOUNT} -J ${JOB_TITLE} -o ${PROJECTLOG} ${SCRIPT_DIR}/demux-2500.sh ${IN_DIR} ${OUT_DIR} ${BASEMASK} ${UNALIGNED_DIR})

cd ${DEMUX_DIR}/${RUN}/${UNALDIR}
#nohup make -j 8 > nohup.$(date +"%Y%m%d%H%M%S").out 2>&1  #TODO: find out wht this does

# Add stats

log "cgstats add --machine 2500 --unaligned ${UNALDIR} ${DEMUX_DIR}/${RUN}/"
cgstats add --machine 2500 --unaligned ${UNALDIR} ${DEMUX_DIR}/${RUN}/ &>> ${PROJECTLOG}

# create stats files
FC=$(echo ${RUN} | awk 'BEGIN {FS="/"} {split($(NF),arr,"_");print substr(arr[4],2,length(arr[4]))}')
PROJs=$(ls ${DEMUX_DIR}/${RUN}/${UNALDIR}/ | grep Proj)
for PROJ in ${PROJs[@]}; do
    prj=$(echo ${PROJ} | sed 's/Project_//')
    log "cgstats select --project ${prj} ${FC} &> ${DEMUX_DIR}/${RUN}/stats-${prj}-${FC}.txt"
    cgstats select --project ${prj} ${FC} &> ${DEMUX_DIR}/${RUN}/stats-${prj}-${FC}.txt
done

log "rm -f ${DEMUX_DIR}/${RUN}/copycomplete.txt"
rm -f ${DEMUX_DIR}/${RUN}/copycomplete.txt

log "date > ${DEMUX_DIR}/${RUN}/demuxcomplete.txt"
date > ${DEMUX_DIR}/${RUN}/demuxcomplete.txt