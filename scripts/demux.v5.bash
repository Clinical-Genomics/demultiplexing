#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $UNALIGNEDBASE

VERSION=3.42.4

logfile=/home/clinical/LOG/demux.hiseq-clinical-test.log.txt
NOW=$(date +"%Y%m%d%H%M%S")
UNALIGNEDBASE=/home/clinical/DEMUX/
BACKUPDIR=/home/clinical/BACKUP/
BASE=$(echo $1 | awk '{if (substr($0,length($0),1) != "/") {print $0"/"} else {print $0}}')
RUN=$(echo ${BASE} | awk 'BEGIN {FS="/"} {print $(NF-1)}')
BASEMASKBYPASS=$2
mkdir -p ${UNALIGNEDBASE}${RUN}
date > ${UNALIGNEDBASE}${RUN}/started.txt
PROJECTLOG=${UNALIGNEDBASE}${RUN}/projectlog.${NOW}.txt
echo [${NOW}] [${RUN}] ${PROJECTLOG} created by $0 $VERSION >> ${PROJECTLOG}

# transform SampleSheet from Mac to Unix
if [[ ! -e ${BASE}/SampleSheet.ori ]]; then
  cp ${BASE}/SampleSheet.csv ${BASE}/SampleSheet.ori
  grep -qs $'\r\n' ${BASE}/SampleSheet.csv
  if [[ $? -eq 0 ]]; then
      echo 'DOS formatted SampleSheet detected. Converting...'
      sed -i 's/\r//' ${BASE}/SampleSheet.csv
      cp ${BASE}/SampleSheet.csv ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv
  else
      grep -qs $'\r' ${BASE}/SampleSheet.csv
      if [[ $? -eq 0 ]]; then
          echo 'MAC formatted SampleSheet detected. Converting...'
          sed -i 's/\r/\n/' ${BASE}/SampleSheet.csv
          cp ${BASE}/SampleSheet.csv ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv
      fi
  fi
fi

if [ -f ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv ]; then 
  fcinfile=$(awk 'BEGIN {FS=","} {fc=$1} END {print fc}' ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv)
  runfc=$(echo ${BASE} | awk 'BEGIN {FS="_"} {print substr($4,2,9)}')
  if [ ! ${runfc} == ${fcinfile} ]; then 
    echo [${NOW}] [${RUN}] Wrong Flowcell ID in SampleSheet. Exits . . . >> ${logfile}
    echo [${NOW}] [${RUN}] Wrong Flowcell ID in SampleSheet. Exits . . . >> ${PROJECTLOG}
    exit
  fi
else
  echo [${NOW}] [${RUN}] SampleSheet not found! Exits . . . >> ${logfile}
  echo [${NOW}] [${RUN}] SampleSheet not found! Exits . . . >> ${PROJECTLOG}
  exit
fi
echo [${NOW}] [${RUN}] Setup correct, starts demuxing . . . >> ${logfile}
echo [${NOW}] [${RUN}] Setup correct, starts demuxing . . . >> ${PROJECTLOG}

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

if [ $BASEMASKBYPASS ]; then
  case $BASEMASKBYPASS in
    '--d8')      USEBASEMASK=Y101,I8,I8,Y101; UNALDIR=Unaligned1 ;;
    '--s8')      USEBASEMASK=Y101,I8,Y101; UNALDIR=Unaligned2 ;;
    '--s6s8')    USEBASEMASK=Y101,I6nn,Y101 ; UNALDIR=Unaligned3 ;;
    '--s6')      USEBASEMASK=Y101,I6n,Y101 ; UNALDIR=Unaligned ;;
    '--s6d8')    USEBASEMASK=Y101,I6nn,nnnnnnnn,Y101 ; UNALDIR=Unaligned4 ;;
    '--s8d8')    USEBASEMASK=Y101,I8,nnnnnnnn,Y101 ; UNALDIR=Unaligned5 ;;
    '--s8n')     USEBASEMASK=Y101,I8n,Y101 ; UNALDIR=Unaligned6
    '--s8nn9')   USEBASEMASK=Y101,I8n,n9,Y101 ; UNALDIR=Unaligned7 ;;
    '--ho')      USEBASEMASK=Y126,I8,Y126 ; UNALDIR=Unaligned ;;
    '--hod8')    USEBASEMASK=Y126,I8,I8,Y126 ; UNALDIR=Unaligned8 ;;
    '--hos8d8')  USEBASEMASK=Y126,I8,n8,Y126 ; UNALDIR=Unaligned9 ;;
    '--hos6d8')  USEBASEMASK=Y126,I6nn,n8,Y126 ; UNALDIR=Unaligned10 ;;
    '--sr51d8')  USEBASEMASK=Y51,I8,I8 ; UNALDIR=Unaligned11 ;;
    '--hos6')    USEBASEMASK=Y126,I6n,Y126 ; UNALDIR=Unaligned12 ;;
    *)    >&2 echo "'$BASEMASKBYPASS' not recognized!"
          >&2 echo "Available options are:"
          >&2 echo "--s6 single 6 index"
          >&2 echo "--s6s8 single 6 advertised as single 8 index"
          >&2 echo "--s6d8 single 6 index advertised as dual 8 index"
          >&2 echo "--s8 single 8 index"
          >&2 echo "--d8 dual 8 index"
          >&2 echo "--s8d8 single 8 index advertised as dual 8 index"
          >&2 echo "--s8n single 8 index advertised as single 9 index"
          >&2 echo "--s8nn9 single 8 index advertised as dual 9 index"
          >&2 echo "--ho High Output run"
          >&2 echo "--hod8 High Output run with dual8 index"
          >&2 echo "--hos8d8 High Output run with single 8 index advertised as dual 8 index"
          >&2 echo "--hos6d8 High Output run with single 6 index advertised as dual 8 index"
          >&2 echo "--hos6 High Output run with single 6 index"
          >&2 echo "--sr51d8 Single Read run (51cycles) with dual 8 index" ;;
  esac
fi

#USEBASEMASK=
# uncomment to check USEBASEMASK
#echo $BASE $RUN
#echo idc1 ${indexread1count}
#echo idc2 ${indexread2count}
#echo USE ${USEBASEMASK}
#exit 22


/usr/local/bin/configureBclToFastq.pl --sample-sheet ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${USEBASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}Data/Intensities/BaseCalls --output-dir ${UNALIGNEDBASE}${RUN}/${UNALDIR} >> ${logfile}
cd ${UNALIGNEDBASE}${RUN}/${UNALDIR}
echo [${NOW}] [${RUN}] Starting  . . .  /usr/local/bin/configureBclToFastq.pl >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --sample-sheet ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --ignore-missing-bcl --ignore-missing-stats >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --use-bases-mask ${USEBASEMASK} --fastq-cluster-count 0 >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --input-dir ${BASE}Data/Intensities/BaseCalls >> ${PROJECTLOG}
echo [${NOW}] [${RUN}]  --output-dir ${UNALIGNEDBASE}${RUN}/${UNALDIR} >> ${PROJECTLOG}
nohup make -j 8 > nohup.${NOW}.out 2>&1

NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] [${RUN}] Demultiplexing finished,  adding stats to clinstatsdb . . . >> ${logfile}
echo [${NOW}] [${RUN}] Demultiplexing finished,  adding stats to clinstatsdb . . .  >> ${PROJECTLOG}
/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/parsedemux.py /home/clinical/DEMUX/${RUN}/ ${UNALDIR}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] "/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/parsedemux.py /home/clinical/DEMUX/${RUN}/ ${UNALDIR}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv" >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] /home/clinical/DEMUX/${RUN}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}

FC=$(echo ${BASE} | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
PROJs=$(ls ${UNALIGNEDBASE}${RUN}/${UNALDIR}/ | grep Proj)
for PROJ in ${PROJs[@]};do
  prj=$(echo ${PROJ} | sed 's/Project_//')
  /home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/selectdemux.py ${prj} ${FC} > ${UNALIGNEDBASE}${RUN}/stats-${prj}-${FC}.txt
  echo "/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/selectdemux.py ${prj} ${FC} ~/.alt_test_db >> ${UNALIGNEDBASE}${RUN}/stats-${prj}-${FC}.txt" >> ${PROJECTLOG}
done

NOW=$(date +"%Y%m%d%H%M%S")
#    copy the demultiplexed files to rasta

# skip NIPT runs
grep -qs Description,cfDNAHiSeqv1.0 ${UNALIGNEDBASE}${RUN}/SampleSheet.csv
if [[ $? -ne 0 ]]; then
  echo [${NOW}] [${RUN}] copy to cluster [rsync -r -t -e ssh ${UNALIGNEDBASE}${RUN} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/] >> ${PROJECTLOG}
  
  rsync -r -t -e ssh ${UNALIGNEDBASE}${RUN} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/
  rc=$?
  NOW=$(date +"%Y%m%d%H%M%S")
  if [[ ${rc} != 0 ]] ; then
    echo [${NOW}] [${RUN}] rsync to rasta failed: Error code: ${rc} >> ${logfile}
    echo [${NOW}] [${RUN}] rsync to rasta failed: Error code: ${rc} >> ${PROJECTLOG}
  else 
    date > ${UNALIGNEDBASE}${RUN}/copycomplete.txt
    scp ${UNALIGNEDBASE}${RUN}/copycomplete.txt rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}
    echo [${NOW}] [${RUN}] scp ${UNALIGNEDBASE}${RUN}/copycomplete.txt rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN} >> ${PROJECTLOG}
    ssh rastapopoulos.scilifelab.se "chmod g+w /mnt/hds/proj/bioinfo/DEMUX/${RUN}"
    echo [${NOW}] [${RUN}] ssh rastapopoulos.scilifelab.se "chmod g+w /mnt/hds/proj/bioinfo/DEMUX/${RUN}" >> ${PROJECTLOG}
    echo [${NOW}] [${RUN}] scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN} >> ${PROJECTLOG}
    echo [${NOW}] [${RUN}] DEMUX transferred, script ends >> ${logfile}
    echo [${NOW}] [${RUN}] DEMUX transferred, script ends >> ${PROJECTLOG}
    scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}
  fi
fi

# the file copycomplete.txt shows that the copy is done
#   can be used on RASTA to start downstream processing

