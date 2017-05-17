#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $DEMUX_DIR

set -eu -o pipefail

VERSION=4.0.0

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

# some sanity checking
if [ -f ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv ]; then 
    fcinfile=$(awk 'BEGIN {FS=","} {fc=$1} END {print fc}' ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv)
    runfc=$(echo ${RUN} | awk 'BEGIN {FS="/"} {split($(NF),arr,"_");print substr(arr[4],2,length(arr[4]))}')
    if [ ! ${runfc} == ${fcinfile} ]; then 
        log "Wrong Flowcell ID in SampleSheet. Exit . . ."
        exit 1
    fi
fi

# here we go!
log "Setup correct, starts demuxing . . ."

# get the index lengths
SAMPLE_INDEX=( $(cat ${BASE}/SampleSheet.csv | sed -n "2p" | sed -e 's/,/\n/g' ) )
SAMPLE_INDEX=( $( echo ${SAMPLE_INDEX[4]} | sed -e 's/-/\n/g' ) )
LEN_SAMPLE_INDEX1=${#SAMPLE_INDEX[0]}
LEN_SAMPLE_INDEX2=${#SAMPLE_INDEX[1]}

# determine index length of run
indexread1count=$(grep IndexRead1 ${BASE}/runParameters.xml | sed 's/<\/IndexRead1>\r//' | sed 's/    <IndexRead1>//')
indexread2count=$(grep IndexRead2 ${BASE}/runParameters.xml | sed 's/<\/IndexRead2>\r//' | sed 's/    <IndexRead2>//')
LEN_Y1=$(grep \<Read1\> ${BASE}/runParameters.xml | sed 's/<\/Read1>\r//' | sed 's/    <Read1>//')
LEN_Y2=$(grep \<Read2\> ${BASE}/runParameters.xml | sed 's/<\/Read2>\r//' | sed 's/    <Read2>//')

# determine index1 length
# http://stackoverflow.com/a/5349772/322188
I1n=$(head -c $(( ${indexread1count} - ${LEN_SAMPLE_INDEX1} )) < /dev/zero | tr '\0' 'n') # print 'n' n times
I1="I${LEN_SAMPLE_INDEX1}${I1n}"
I2=''

# determine index2 length
if [[ ${indexread2count} -gt 0 ]]; then # dual
    if [[ ${LEN_SAMPLE_INDEX2} -gt 0 ]]; then
        I2="I${LEN_SAMPLE_INDEX2}"
    fi
    I2n=$(head -c $(( ${indexread2count} - ${LEN_SAMPLE_INDEX2} )) < /dev/zero | tr '\0' 'n') # print 'n' n times
    I2=",${I2}${I2n}"
fi

# determine read2
Y1=Y${LEN_Y1}
Y2=
if [[ ${LEN_Y2} -gt 0 ]]; then
    Y2=,Y${LEN_Y2}
fi

# put the basemask together
BASEMASK="${Y1},${I1}${I2}${Y2}"
UNALDIR=Unaligned-${BASEMASK//,}

# DEMUX !
log "/usr/local/bin/configureBclToFastq.pl --force --sample-sheet ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${BASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}/Data/Intensities/BaseCalls --output-dir ${DEMUX_DIR}/${RUN}/${UNALDIR}"
# the sed command is there to remove the color codes out of the demux output and create a pretty log file
/usr/local/bin/configureBclToFastq.pl --force --sample-sheet ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${BASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}/Data/Intensities/BaseCalls --output-dir ${DEMUX_DIR}/${RUN}/${UNALDIR} 2>&1 | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g" >> ${PROJECTLOG}

cd ${DEMUX_DIR}/${RUN}/${UNALDIR}
nohup make -j 8 > nohup.${NOW}.out 2>&1

# Add stats
log "/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/parsedemux.py ${DEMUX_DIR}/${RUN}/ ${UNALDIR}/ ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv"
/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/parsedemux.py ${DEMUX_DIR}/${RUN}/ ${UNALDIR}/ ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}
/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/parsedemux.py ${DEMUX_DIR}/${RUN}/ ${UNALDIR}/ ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv ~/.scilifelabrc_aws >> ${PROJECTLOG}

# create stats files
FC=$(echo ${RUN} | awk 'BEGIN {FS="/"} {split($(NF),arr,"_");print substr(arr[4],2,length(arr[4]))}')
PROJs=$(ls ${DEMUX_DIR}/${RUN}/${UNALDIR}/ | grep Proj)
for PROJ in ${PROJs[@]};do
    prj=$(echo ${PROJ} | sed 's/Project_//')
    log "/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/selectdemux.py ${prj} ${FC} >> ${DEMUX_DIR}/${RUN}/stats-${prj}-${FC}.txt"
    /home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/selectdemux.py ${prj} ${FC} > ${DEMUX_DIR}/${RUN}/stats-${prj}-${FC}.txt
done

# skip NIPT runs
set +e
if ! grep -qs Description,cfDNAHiSeqv1.0 ${DEMUX_DIR}/${RUN}/SampleSheet.csv; then
    set -e
    log "rsync -r -t -e ssh ${DEMUX_DIR}/${RUN} ${DEST_SERVER}:${DEST_DIR}"
    rsync -r -t -e ssh ${DEMUX_DIR}/${RUN} ${DEST_SERVER}:${DEST_DIR}

    date > ${DEMUX_DIR}/${RUN}/copycomplete.txt

    log "scp ${DEMUX_DIR}/${RUN}/copycomplete.txt ${DEST_SERVER}:${DEST_DIR}/${RUN}"
    scp ${DEMUX_DIR}/${RUN}/copycomplete.txt ${DEST_SERVER}:${DEST_DIR}/${RUN}
    log "ssh ${DEST_SERVER} "chmod g+w ${DEST_DIR}/${RUN}""
    ssh ${DEST_SERVER} "chmod g+w ${DEST_DIR}/${RUN}"
    log "scp ${PROJECTLOG} ${DEST_SERVER}:${DEST_DIR}/${RUN}"
    scp ${PROJECTLOG} ${DEST_SERVER}:${DEST_DIR}/${RUN}

    log "DEMUX transferred, script ends"
fi
