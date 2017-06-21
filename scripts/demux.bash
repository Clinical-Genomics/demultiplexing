#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $DEMUX_DIR

set -eu -o pipefail

shopt -s expand_aliases
source /home/clinical/SCRIPTS/demux.functions

VERSION=4.6.4

##########
# PARAMS #
##########

BASE=${1?'please provide a run dir'}
EMAIL=kenny.billiau@scilifelab.se
DEMUX_DIR=/home/clinical/DEMUX/
DEST_SERVER=rastapopoulos
DEST_DIR=/mnt/hds/proj/bioinfo/DEMUX/

RUN=$(basename ${BASE})
RUN_DIR=$(dirname ${BASE})
PROJECTLOG=${DEMUX_DIR}/${RUN}/projectlog.$(date +"%Y%m%d%H%M%S").txt

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

########
# MAIN #
########

set +e
if ! grep -qs Description,cfDNAHiSeqv1.0 ${DEMUX_DIR}/${RUN}/SampleSheet.csv; then
    log "${RUN} is NIPT - skipping"
    exit 0
fi
set -e

# init
mkdir -p ${DEMUX_DIR}/${RUN}
log "${PROJECTLOG} created by $0 $VERSION"
date > ${DEMUX_DIR}/${RUN}/started.txt

# transform SampleSheet from Mac to Unix
if [[ ! -e ${BASE}/SampleSheet.ori ]]; then
    cp ${BASE}/SampleSheet.csv ${BASE}/SampleSheet.ori
    set +e
    if grep -qs $'\r' ${BASE}/SampleSheet.csv; then
        set -e
        sed -i 's//\n/g' ${BASE}/SampleSheet.csv
    fi
    sed -i '/^$/d' ${BASE}/SampleSheet.csv # remove empty lines
    cp ${BASE}/SampleSheet.csv ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv
fi

## some sanity checking
#if [[ -f ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv ]]; then 
#    fcinfile=$(awk 'BEGIN {FS=","} {fc=$1} END {print fc}' ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv)
#    runfc=$( basename ${RUN} | awk 'BEGIN {FS="_"} {print $NF}')
#    if [[ ! ${runfc} == ${fcinfile} ]]; then 
#        log "Wrong Flowcell ID in SampleSheet. Exit . . ."
#        exit 1
#    fi
#fi

# here we go!
log "Setup correct, starts demuxing . . ."

echo $(get_basemask ${BASE})
BASEMASK=$(get_basemask ${BASE})
UNALDIR=Unaligned-${BASEMASK//,}

# DEMUX !
log "/usr/local/bin/configureBclToFastq.pl --force --sample-sheet ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${BASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}/Data/Intensities/BaseCalls --output-dir ${DEMUX_DIR}/${RUN}/${UNALDIR}"
# the sed command is there to remove the color codes out of the demux output and create a pretty log file
/usr/local/bin/configureBclToFastq.pl --force --sample-sheet ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${BASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}/Data/Intensities/BaseCalls --output-dir ${DEMUX_DIR}/${RUN}/${UNALDIR} 2>&1 | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g" >> ${PROJECTLOG}

cd ${DEMUX_DIR}/${RUN}/${UNALDIR}
nohup make -j 8 > nohup.$(date +"%Y%m%d%H%M%S").out 2>&1

# Add stats

log "cgstats add --machine 2500 --unaligned ${UNALDIR} ${DEMUX_DIR}/${RUN}/" >> ${PROJECT_LOG}
cgstats add --machine 2500 --unaligned ${UNALDIR} ${DEMUX_DIR}/${RUN}/ &>> ${PROJECT_LOG}

# create stats files
FC=$(echo ${RUN} | awk 'BEGIN {FS="/"} {split($(NF),arr,"_");print substr(arr[4],2,length(arr[4]))}')
PROJs=$(ls ${DEMUX_DIR}/${RUN}/${UNALDIR}/ | grep Proj)
for PROJ in ${PROJs[@]};do
    prj=$(echo ${PROJ} | sed 's/Project_//')
    log "cgstats select --project ${prj} ${FC} &> ${DEMUX_DIR}/${RUN}/stats-${prj}-${FC}.txt" >> ${PROJECT_LOG}
    cgstats select --project ${prj} ${FC} &> ${DEMUX_DIR}/${RUN}/stats-${prj}-${FC}.txt
done

log "rsync -r -t -e ssh ${DEMUX_DIR}/${RUN} ${DEST_SERVER}:${DEST_DIR}"
rsync -r -t -e ssh ${DEMUX_DIR}/${RUN} ${DEST_SERVER}:${DEST_DIR}
log "scp ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv ${DEST_SERVER}:${DEST_DIR}/${RUN}/"
scp ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv ${DEST_SERVER}:${DEST_DIR}/${RUN}/
date > ${DEMUX_DIR}/${RUN}/copycomplete.txt
log "scp ${DEMUX_DIR}/${RUN}/copycomplete.txt ${DEST_SERVER}:${DEST_DIR}/${RUN}"
scp ${DEMUX_DIR}/${RUN}/copycomplete.txt ${DEST_SERVER}:${DEST_DIR}/${RUN}
log "ssh ${DEST_SERVER} 'chmod g+w ${DEST_DIR}/${RUN}'"
ssh ${DEST_SERVER} "chmod g+w ${DEST_DIR}/${RUN}"
log "scp ${PROJECTLOG} ${DEST_SERVER}:${DEST_DIR}/${RUN}"
scp ${PROJECTLOG} ${DEST_SERVER}:${DEST_DIR}/${RUN}

log "DEMUX transferred, script ends"
