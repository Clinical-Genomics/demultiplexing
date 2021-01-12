#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $UNALIGNEDBASE

set -eu -o pipefail
VERSION=5.4.2
shopt -s expand_aliases
. ~/.bashrc

##########
# PARAMS #
##########

BASE=${1?'please provide a run dir'}

EMAIL=kenny.billiau@scilifelab.se
DEMUX_DIR=/home/hiseq.clinical/NIPT_DEMUX/

SCRIPT_DIR=$(dirname $0)
RUN=$(basename ${BASE})
RUN_DIR=$(dirname ${BASE})
PROJECTLOG=${DEMUX_DIR}/${RUN}/projectlog.$(date +"%Y%m%d%H%M%S").txt

#############
# FUNCTIONS #
#############

log() {
    NOW=$(date +"%Y%m%d%H%M%S")
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

mkdir -p ${DEMUX_DIR}/${RUN}

cp ${BASE}/SampleSheet.ori ${BASE}/SampleSheet.csv
if grep -qs $'\r' ${BASE}/SampleSheet.csv; then
    sed -i 's//\n/g' ${BASE}/SampleSheet.csv
fi
sed -i '/^$/d' ${BASE}/SampleSheet.csv # remove empty lines

log "demux sheet demux -a nipt ${BASE}/SampleSheet.csv > ${BASE}/SampleSheet.mas"
demux sheet demux -a nipt ${BASE}/SampleSheet.csv > ${BASE}/SampleSheet.mas
mv ${BASE}/SampleSheet.mas ${BASE}/SampleSheet.csv
cp ${BASE}/SampleSheet.csv ${BASE}/Data/Intensities/BaseCalls/

log "bash ${SCRIPT_DIR}/demux.bash ${BASE} ${DEMUX_DIR}"
bash ${SCRIPT_DIR}/demux.bash ${BASE} ${DEMUX_DIR}

