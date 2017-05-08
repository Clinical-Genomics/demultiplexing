#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $DEMUX_DIR

VERSION=3.44.7

##########
# PARAMS #
##########

BASE=${1?'please provide a run dir'}
BASEMASKBYPASS=$2 # optional basemask option

DEMUX_DIR=/home/clinical/DEMUX/
RUN=$(basename ${BASE})
PROJECTLOG=${DEMUX_DIR}/${RUN}/projectlog.$(date +"%Y%m%d%H%M%S").txt

#############
# FUNCTIONS #
#############

log() {
    NOW=$(date +"%Y%m%d%H%M%S")
    (>&2 echo [$NOW] $@) >> $PROJECTLOG
}

########
# MAIN #
########

log ${PROJECTLOG} created by $0 $VERSION

# init
mkdir -p ${DEMUX_DIR}/${RUN}
date > ${DEMUX_DIR}/${RUN}/started.txt

# transform SampleSheet from Mac to Unix
if [[ ! -e ${BASE}/SampleSheet.ori ]]; then
  cp ${BASE}/SampleSheet.csv ${BASE}/SampleSheet.ori
  if grep -qs $'\r' ${BASE}/SampleSheet.csv; then
    sed -i 's//\n/g' ${BASE}/SampleSheet.csv
  fi
  sed -i '/^$/d' ${BASE}/SampleSheet.csv # remove empty lines
  cp ${BASE}/SampleSheet.csv ${BASE}/Data/Intensities/BaseCalls/SampleSheet.csv
fi

# some sanity checking
if [ -f ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv ]; then 
  fcinfile=$(awk 'BEGIN {FS=","} {fc=$1} END {print fc}' ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv)
  runfc=$(echo ${BASE} | awk 'BEGIN {FS="_"} {print substr($4,2,9)}')
  if [ ! ${runfc} == ${fcinfile} ]; then 
    log "Wrong Flowcell ID in SampleSheet. Exit . . ."
    exit
  fi
fi

# here we go!
log "Setup correct, starts demuxing . . ."

# create the basemask
SAMPLE_INDEX=( $(cat ${BASE}/SampleSheet.csv | sed -n "2p" | sed -e 's/,/\n/g' ) )
SAMPLE_INDEX=( $( echo ${SAMPLE_INDEX[4]} | sed -e 's/-/\n/g' ) )
LEN_SAMPLE_INDEX1=${#SAMPLE_INDEX[0]}
LEN_SAMPLE_INDEX2=${#SAMPLE_INDEX[1]}

# Determine index length of run
indexread1count=$(grep IndexRead1 ${BASE}/runParameters.xml | sed 's/<\/IndexRead1>\r//' | sed 's/    <IndexRead1>//')
indexread2count=$(grep IndexRead2 ${BASE}/runParameters.xml | sed 's/<\/IndexRead2>\r//' | sed 's/    <IndexRead2>//')
LEN_Y1=$(grep \<Read1\> ${BASE}/runParameters.xml | sed 's/<\/Read1>\r//' | sed 's/    <Read1>//')
LEN_Y2=$(grep \<Read2\> ${BASE}/runParameters.xml | sed 's/<\/Read2>\r//' | sed 's/    <Read2>//')

# Determine Basemask
# http://stackoverflow.com/a/5349772/322188
I1n=$(head -c $(( ${indexread1count} - ${LEN_SAMPLE_INDEX1} )) < /dev/zero | tr '\0' 'n') # print 'n' n times
I1="I${LEN_SAMPLE_INDEX1}${I1n}"
I2=''

if [[ ${indexread2count} -gt 0 ]]; then # dual
    if [[ ${LEN_SAMPLE_INDEX2} -gt 0 ]]; then
        I2="I${LEN_SAMPLE_INDEX2}"
    fi
    I2n=$(head -c $(( ${indexread2count} - ${LEN_SAMPLE_INDEX2} )) < /dev/zero | tr '\0' 'n') # print 'n' n times
    I2=",${I2}${I2n}"
fi

Y1=Y${LEN_Y1}
if [[ ${LEN_Y2} -gt 0 ]]; then
    Y2=,Y${LEN_Y2}
fi

BASEMASK="${Y1},${I1}${I2}${Y2}"
UNALDIR=Unaligned

# DEMUX !
/usr/local/bin/configureBclToFastq.pl --sample-sheet ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${USEBASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}Data/Intensities/BaseCalls --output-dir ${DEMUX_DIR}${RUN}/${UNALDIR}
log "/usr/local/bin/configureBclToFastq.pl --sample-sheet ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${USEBASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}Data/Intensities/BaseCalls --output-dir ${DEMUX_DIR}${RUN}/${UNALDIR}" >> ${PROJECTLOG}

cd ${DEMUX_DIR}${RUN}/${UNALDIR}
nohup make -j 8 > nohup.${NOW}.out 2>&1

# Add stats
log "Demultiplexing finished,  adding stats to clinstatsdb . . ."
/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/parsedemux.py /home/clinical/DEMUX/${RUN}/ ${UNALDIR}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}
/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/parsedemux.py /home/clinical/DEMUX/${RUN}/ ${UNALDIR}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv ~/.scilifelabrc_aws >> ${PROJECTLOG}
log "/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/parsedemux.py /home/clinical/DEMUX/${RUN}/ ${UNALDIR}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv"
log "/home/clinical/DEMUX/${RUN}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv"

# create stats files
FC=$(echo ${BASE} | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
PROJs=$(ls ${DEMUX_DIR}${RUN}/${UNALDIR}/ | grep Proj)
for PROJ in ${PROJs[@]};do
  prj=$(echo ${PROJ} | sed 's/Project_//')
  echo "/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/selectdemux.py ${prj} ${FC} >> ${DEMUX_DIR}${RUN}/stats-${prj}-${FC}.txt" >> ${PROJECTLOG}
  /home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/selectdemux.py ${prj} ${FC} > ${DEMUX_DIR}${RUN}/stats-${prj}-${FC}.txt
done

# skip NIPT runs
if ! grep -qs Description,cfDNAHiSeqv1.0 ${DEMUX_DIR}${RUN}/SampleSheet.csv; then
  log "rsync -r -t -e ssh ${DEMUX_DIR}${RUN} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/"
  
  # sync results to rasta
  if rsync -r -t -e ssh ${DEMUX_DIR}${RUN} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/; then
    log "rsync to rasta failed: Error code: $?"
  else 
    date > ${DEMUX_DIR}${RUN}/copycomplete.txt
    log "scp ${DEMUX_DIR}${RUN}/copycomplete.txt rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}"
    scp ${DEMUX_DIR}${RUN}/copycomplete.txt rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}
    log "ssh rastapopoulos.scilifelab.se \"chmod g+w /mnt/hds/proj/bioinfo/DEMUX/${RUN}\""
    ssh rastapopoulos.scilifelab.se "chmod g+w /mnt/hds/proj/bioinfo/DEMUX/${RUN}"
    log "scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}"
    scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}
    log "DEMUX transferred, script ends"
  fi
fi
