#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $UNALIGNEDBASE
#
#   v5 [20150203]    added 88n basemask
#      [20150202]    added basemask selecting param
#      [20150121]    added six2eight param
#      [20140911]    adding project log
#      [20140729]    changed clinstatsdb to the instance on hippocampus
#      [20140311]    added dual index handler for 8 + 8 bases
#      [20140310]    to handle _either_ I6n or I8, v3ic   for  index choice
#      [20140310]    made v3 for 8 cycle index
#      [20140205]    removed cerebellum stuff added --fastq-cluster-count 0 again
#      [20140204]    added file copy to cerebellum when demux done, removed entry below
#      [20140203]    added --fastq-cluster-count 0, to specify single fastq file
#   v2 [20140108]    took away parts that should be run on the cluster
#                    now demultiplexing is run, stats added to db and 
#                    demux-files copied to the cluster . . .
#       
#
logfile=/home/clinical/LOG/demux.hiseq-clinical.log.txt
NOW=$(date +"%Y%m%d%H%M%S")
UNALIGNEDBASE=/home/clinical/DEMUX/
BACKUPDIR=/home/clinical/BACKUP/
BASE=$(echo $1 | awk '{if (substr($0,length($0),1) != "/") {print $0"/"} else {print $0}}')
RUN=$(echo ${BASE} | awk 'BEGIN {FS="/"} {print $(NF-1)}')
BASEMASKBYPASS=$2
mkdir -p ${UNALIGNEDBASE}${RUN}
PROJECTLOG=${UNALIGNEDBASE}${RUN}/projectlog.${NOW}.txt
echo [${NOW}] [${RUN}] ${PROJECTLOG} created by $0 >> ${PROJECTLOG}
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
  else
    >&2 echo "'$BASEMASKBYPASS' not recognized!"
    >&2 echo "Available options are:"
    >&2 echo "--s6 single 6 index"
    >&2 echo "--s6s8 single 6 advertised as single 8 index"
    >&2 echo "--s6d8 single 6 index advertised as dual 8 index"
    >&2 echo "--s8 single 8 index"
    >&2 echo "--d8 dual 8 index"
    >&2 echo "--s8d8 single 8 index advertised as dual 8 index"
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


/usr/local/bin/configureBclToFastq.pl --sample-sheet ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv --use-bases-mask ${USEBASEMASK} --fastq-cluster-count 0 --input-dir ${BASE}Data/Intensities/BaseCalls --output-dir ${UNALIGNEDBASE}${RUN}/${UNALDIR} >> ${logfile}
cd ${UNALIGNEDBASE}${RUN}/${UNALDIR}
echo [${NOW}] [${RUN}] Starting  . . .  /usr/local/bin/configureBclToFastq.pl >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --sample-sheet ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --use-bases-mask ${USEBASEMASK} --fastq-cluster-count 0 >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] --input-dir ${BASE}Data/Intensities/BaseCalls >> ${PROJECTLOG}
echo [${NOW}] [${RUN}]  --output-dir ${UNALIGNEDBASE}${RUN}/${UNALDIR} >> ${PROJECTLOG}
nohup make -j 8 > nohup.${NOW}.out 2>&1

NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] [${RUN}] Demultiplexing finished,  adding stats to clinstatsdb . . . >> ${logfile}
echo [${NOW}] [${RUN}] Demultiplexing finished,  adding stats to clinstatsdb . . .  >> ${PROJECTLOG}
bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/parseunaligned_dbserver.py /home/clinical/DEMUX/${RUN}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv
# # # # the new python script for parsing using demux table
python /home/clinical/git/rikard/demultiplexing/scripts/parsedemux.py /home/clinical/DEMUX/${RUN}/ ${UNALDIR}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv ~/.alt_test_db
echo [${NOW}] [${RUN}] bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/parseunaligned_dbserver.py >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] /home/clinical/DEMUX/${RUN}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}

FC=$(echo ${BASE} | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
PROJs=$(ls ${UNALIGNEDBASE}${RUN}/Unaligned/ | grep Proj)
for PROJ in ${PROJs[@]};do
  prj=$(echo ${PROJ} | sed 's/Project_//')
  bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/selectunaligned_dbserver.py ${prj} ${FC} > ${UNALIGNEDBASE}${RUN}/stats-${prj}-${FC}.txt
  # # # # the new python script for parsing using demux table
  python /home/clinical/git/rikard/demultiplexing/scripts/selectdemux.py ${prj} ${FC} ~/.alt_test_db > ${UNALIGNEDBASE}${RUN}/${UNALDIR}/stats-${prj}-${FC}.txt
  echo [${NOW}] [${RUN}] bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/selectunaligned_dbserver.py >> ${PROJECTLOG}
  echo "[${NOW}] [${RUN}] ${prj} ${FC} > ${UNALIGNEDBASE}${RUN}/stats-${prj}-${FC}.txt" >> ${PROJECTLOG}
done

NOW=$(date +"%Y%m%d%H%M%S")
#    copy the demultiplexed files to rasta

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
#  scp ${UNALIGNEDBASE}${RUN}/copycomplete.txt cerebellum.scilifelab.se:/home/hiseq.clinical/Runs/${RUN}/demuxdone.txt
  echo [${NOW}] [${RUN}] scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN} >> ${PROJECTLOG}
  echo [${NOW}] [${RUN}] DEMUX transferred, script ends >> ${logfile}
  echo [${NOW}] [${RUN}] DEMUX transferred, script ends >> ${PROJECTLOG}
  scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}
fi



# the file copycomplete.txt shows that the copy is done
#   can be used on RASTA to start downstream processing

