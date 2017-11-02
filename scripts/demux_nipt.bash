#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $UNALIGNEDBASE

set -eu -o pipefail

VERSION=4.11.2

##########
# PARAMS #
##########

BASE=${1?'please provide a run dir'}

EMAIL=kenny.billiau@scilifelab.se
DEMUX_DIR=/home/clinical/DEMUX/
DEST_SERVER=rastapopoulos
DEST_DIR=/mnt/hds/proj/bioinfo/DEMUX/

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

cp ${BASE}/SampleSheet.csv ${BASE}/SampleSheet.ori
log "/home/clinical/SCRIPTS/massagenipt.py ${BASE}/SampleSheet.csv nuru > ${BASE}/SampleSheet.mas"
/home/clinical/SCRIPTS/massagenipt.py ${BASE}/SampleSheet.csv nuru > ${BASE}/SampleSheet.mas
mv ${BASE}/SampleSheet.mas ${BASE}/SampleSheet.csv
cp ${BASE}/SampleSheet.csv ${BASE}/Data/Intensities/BaseCalls/

log "bash ${SCRIPT_DIR}/demux.v5.bash ${BASE}"
bash ${SCRIPT_DIR}/demux.v5.bash ${BASE}
