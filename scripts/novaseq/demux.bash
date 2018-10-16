#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $DEMUX_DIR

set -eu -o pipefail

shopt -s expand_aliases
source $HOME/.bashrc
source $HOME/SCRIPTS/demux.functions

VERSION=4.23.0

##########
# PARAMS #
##########

BASE=${1?'please provide a run dir'}
DEMUX_DIR=${2?'please provide a demux dir'}

RUN=$(basename ${BASE})
RUN_DIR=$(dirname ${BASE})

#############
# FUNCTIONS #
#############

log() {
    local NOW=$(date +"%Y%m%d%H%M%S")
    echo "[$NOW] $@"
}

###########
# PREMAIN #
###########

# transform SampleSheet from Mac to Unix
if [[ ! -e ${BASE}/SampleSheet.ori ]]; then
    cp ${BASE}/SampleSheet.csv ${BASE}/SampleSheet.ori
    if grep -qs $'\r' ${BASE}/SampleSheet.csv; then
        sed -i 's//\n/g' ${BASE}/SampleSheet.csv
    fi
    sed -i '/^$/d' ${BASE}/SampleSheet.csv # remove empty lines
fi

########
# MAIN #
########

# init
mkdir -p ${DEMUX_DIR}/${RUN}

# log the version
/usr/local/bcl2fastq2/bin/bcl2fastq --version

# here we go!
log "Here we go!"

echo $(get_basemask ${BASE})
BASEMASK=$(get_basemask ${BASE})
UNALDIR=Unaligned-${BASEMASK//,}

# DEMUX !
log "/usr/local/bcl2fastq2/bin/bcl2fastq --loading-threads 3 --processing-threads 12 --writing-threads 3 --output-dir /demux/180619_A00187_0036_BHFM5JDMXX_dual8 --use-bases-mask Y151,I8NNNNNNNNN,I8,Y147 --sample-sheet HFM5JDMXX-samplesheet.csv"

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
