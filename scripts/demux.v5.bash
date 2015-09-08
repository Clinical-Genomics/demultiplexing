#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $UNALIGNEDBASE

VERSION=3.21.11

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
## ## ## ## ## ## ## ## if [ -f hejhopp.sko ]; then ######### to block out code in-between
if [ -f ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv ]; then 
  fcinfile=$(awk 'BEGIN {FS=","} {fc=$1} END {print fc}' ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv)
  runfc=$(echo ${BASE} | awk 'BEGIN {FS="_"} {print substr($4,2,9)}')
#  echo runfc ${runfc} fcinfile ${fcinfile}  
  if [ ! ${runfc} == ${fcinfile} ]; then 
#    echo Flowcell ID is correct, continues . . .
#  else
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

## ## ## ## ## ## ## fi ##################### end if hejhop

if [ $BASEMASKBYPASS ]; then
  if [ $BASEMASKBYPASS == '--d8' ]; then
    USEBASEMASK=Y101,I8,I8,Y101
    UNALDIR=Unaligned1
  elif [ $BASEMASKBYPASS == '--s8' ]; then
    USEBASEMASK=Y101,I8,Y101
    UNALDIR=Unaligned2
  elif [ $BASEMASKBYPASS == '--s6s8' ]; then
    USEBASEMASK=Y101,I6nn,Y101
    UNALDIR=Unaligned3
  elif [ $BASEMASKBYPASS == '--s6' ]; then
    USEBASEMASK=Y101,I6n,Y101
    UNALDIR=Unaligned
  elif [ $BASEMASKBYPASS == '--s6d8' ]; then
    USEBASEMASK=Y101,I6nn,nnnnnnnn,Y101
    UNALDIR=Unaligned4
  elif [ $BASEMASKBYPASS == '--s8d8' ]; then
    USEBASEMASK=Y101,I8,nnnnnnnn,Y101
    UNALDIR=Unaligned5
  elif [ $BASEMASKBYPASS == '--s8n' ]; then
    USEBASEMASK=Y101,I8n,Y101
    UNALDIR=Unaligned6
  elif [ $BASEMASKBYPASS == '--s8nn9' ]; then
    USEBASEMASK=Y101,I8n,n9,Y101
    UNALDIR=Unaligned7
  elif [ $BASEMASKBYPASS == '--ho' ]; then
    USEBASEMASK=Y126,I8,Y126
    UNALDIR=Unaligned
  elif [ $BASEMASKBYPASS == '--hod8' ]; then
    USEBASEMASK=Y126,I8,I8,Y126
    UNALDIR=Unaligned8
  elif [ $BASEMASKBYPASS == '--hos8d8' ]; then
    USEBASEMASK=Y126,I8,n8,Y126
    UNALDIR=Unaligned9
  else
    >&2 echo "'$BASEMASKBYPASS' not recognized!"
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
  fi
else
  
  ######   uses windows end-of-line/return setting [=FUCKING stupid!]
  ######
  indexread1count=$(grep IndexRead1 ${BASE}/runParameters.xml | sed 's/<\/IndexRead1>\r//' | sed 's/    <IndexRead1>//')
  indexread2count=$(grep IndexRead2 ${BASE}/runParameters.xml | sed 's/<\/IndexRead2>\r//' | sed 's/    <IndexRead2>//')
  
  #echo ${indexread1count}
  #echo ${indexread2count}
  
  #  start to assume standard singel index
  if [ "${indexread2count}" == 8 ]; then
  #  this is not true if second index equals 8
    USEBASEMASK=Y101,I8,I8,Y101
    UNALDIR=Unaligned1
    echo  ${indexread2count} == "8" ix2
  else
    echo  ${indexread2count} == 8 NOT ix2
    if [ "${indexread1count}" == 8 ]; then
      echo ${indexread1count} == 8
  #  not if first index equals 8 either
        USEBASEMASK=Y101,I8,Y101
        UNALDIR=Unaligned2
    else 
      echo ${indexread1count} == 8 NOT ix1
      USEBASEMASK=Y101,I6n,Y101
      UNALDIR=Unaligned
    fi
  fi
fi

#USEBASEMASK=
# uncomment to check USEBASEMASK
#echo $BASE $RUN
#echo idc1 ${indexread1count}
#echo idc2 ${indexread2count}
#echo USE ${USEBASEMASK}
#exit 22

## ## ## ## ## ## ## ## ## ## if [ -f hejhopp.sko ]; then ######### to block out code in-between


/usr/local/bin/configureBclToFastq.pl --sample-sheet ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv --ignore-missing-bcl --ignore-missing-stats --use-bases-mask ${USEBASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}Data/Intensities/BaseCalls --output-dir ${UNALIGNEDBASE}${RUN}/${UNALDIR} >> ${logfile}
cd ${UNALIGNEDBASE}${RUN}/${UNALDIR}
echo [${NOW}] [${RUN}] Starting  . . .  /usr/local/bin/configureBclToFastq.pl >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --sample-sheet ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --ignore-missing-bcl --ignore-missing-stats >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --use-bases-mask ${USEBASEMASK} --fastq-cluster-count 0 >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --input-dir ${BASE}Data/Intensities/BaseCalls >> ${PROJECTLOG}
echo [${NOW}] [${RUN}]  --output-dir ${UNALIGNEDBASE}${RUN}/${UNALDIR} >> ${PROJECTLOG}
nohup make -j 8 > nohup.${NOW}.out 2>&1

## ## ## ## ## ## ## ## ## ## fi ##################### end if hejhop


NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] [${RUN}] Demultiplexing finished,  adding stats to clinstatsdb . . . >> ${logfile}
echo [${NOW}] [${RUN}] Demultiplexing finished,  adding stats to clinstatsdb . . .  >> ${PROJECTLOG}
bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/parseunaligned_dbserver.py /home/clinical/DEMUX/${RUN}/ ${UNALDIR} /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}
# # # # the new python script for parsing using demux table
/home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/parsedemux.py /home/clinical/DEMUX/${RUN}/ ${UNALDIR}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv ~/.alt_test_db >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/parseunaligned_dbserver.py >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] /home/clinical/DEMUX/${RUN}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}

FC=$(echo ${BASE} | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
PROJs=$(ls ${UNALIGNEDBASE}${RUN}/${UNALDIR}/ | grep Proj)
for PROJ in ${PROJs[@]};do
  prj=$(echo ${PROJ} | sed 's/Project_//')
  bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/selectunaligned_dbserver.py ${prj} ${FC} > ${UNALIGNEDBASE}${RUN}/stats-${prj}-${FC}.txt
  # # # # the new python script for parsing using demux table
  /home/hiseq.clinical/.virtualenv/mysql/bin/python /home/clinical/SCRIPTS/selectdemux.py ${prj} ${FC} ~/.alt_test_db >> ${UNALIGNEDBASE}${RUN}/${UNALDIR}/stats-${prj}-${FC}.txt
  echo [${NOW}] [${RUN}] bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/selectunaligned_dbserver.py >> ${PROJECTLOG}
  echo "[${NOW}] [${RUN}] ${prj} ${FC} > ${UNALIGNEDBASE}${RUN}/stats-${prj}-${FC}.txt" >> ${PROJECTLOG}
done

NOW=$(date +"%Y%m%d%H%M%S")
#    copy the demultiplexed files to rasta

# skip NIPT runs
grep -qs Description,NIPTv1 ${UNALIGNEDBASE}${RUN}/SampleSheet.csv
if [[ $? -ne 0 ]]; then
  echo [${NOW}] [${RUN}] copy to cluster [rsync -r -t -e ssh ${UNALIGNEDBASE}${RUN} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/] >> ${PROJECTLOG}
  
  ## ## ## ## ## ## ## ## ## ## if [ -f hejhopp.sko ]; then ######### to block out code in-between
  
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
  #  scp ${UNALIGNEDBASE}${RUN}/copycomplete.txt cerebellum.scilifelab.se:/home/hiseq.clinical/Runs/${RUN}/demuxdone.txt
    echo [${NOW}] [${RUN}] scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN} >> ${PROJECTLOG}
    echo [${NOW}] [${RUN}] DEMUX transferred, script ends >> ${logfile}
    echo [${NOW}] [${RUN}] DEMUX transferred, script ends >> ${PROJECTLOG}
    scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}
  fi
fi

## ## ## ## ## ## ## ## ## ## fi ##################### end if hejhop


# the file copycomplete.txt shows that the copy is done
#   can be used on RASTA to start downstream processing

