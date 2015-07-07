#!/bin/bash
# When adding statistics to clinstatsdb fails, you can use this script to
# * add the statistics
# * create the stats-*.txt files
# * sync the stats-*.txt files to rasta

VERSION=3.12.2

NOW=$(date +"%Y%m%d%H%M%S")
UNALIGNEDBASE=/home/clinical/DEMUX/
BACKUPDIR=/home/clinical/BACKUP/
BASE=$(echo $1 | awk '{if (substr($0,length($0),1) != "/") {print $0"/"} else {print $0}}')
RUN=$(echo ${BASE} | awk 'BEGIN {FS="/"} {print $(NF-1)}')
BASEMASKBYPASS=$2
PROJECTLOG=${UNALIGNEDBASE}${RUN}/projectlog.${NOW}.txt
echo [${NOW}] [${RUN}] ${PROJECTLOG} created by $0 $VERSION >> ${PROJECTLOG}

if [ $BASEMASKBYPASS ]; then
  if [ $BASEMASKBYPASS == '--d8' ]; then
    UNALDIR=Unaligned1
  elif [ $BASEMASKBYPASS == '--s8' ]; then
    UNALDIR=Unaligned2
  elif [ $BASEMASKBYPASS == '--s6s8' ]; then
    UNALDIR=Unaligned3
  elif [ $BASEMASKBYPASS == '--s6' ]; then
    UNALDIR=Unaligned
  elif [ $BASEMASKBYPASS == '--s6d8' ]; then
    UNALDIR=Unaligned4
  elif [ $BASEMASKBYPASS == '--s8d8' ]; then
    UNALDIR=Unaligned5
  elif [ $BASEMASKBYPASS == '--s8n' ]; then
    UNALDIR=Unaligned6
  elif [ $BASEMASKBYPASS == '--ho' ]; then
    UNALDIR=Unaligned
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
    >&2 echo "--ho High Output run"
  fi
else
  
  ######   uses windows end-of-line/return setting [=FUCKING stupid!]
  ######
  indexread1count=$(grep IndexRead1 ${BASE}/runParameters.xml | sed 's/<\/IndexRead1>\r//' | sed 's/    <IndexRead1>//')
  indexread2count=$(grep IndexRead2 ${BASE}/runParameters.xml | sed 's/<\/IndexRead2>\r//' | sed 's/    <IndexRead2>//')
  
  if [ "${indexread2count}" == 8 ]; then
    UNALDIR=Unaligned1
  else
    if [ "${indexread1count}" == 8 ]; then
      UNALDIR=Unaligned2
    else 
      UNALDIR=Unaligned
    fi
  fi
fi


NOW=$(date +"%Y%m%d%H%M%S")
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
echo [${NOW}] [${RUN}] copy to cluster [rsync -r -t -e ssh ${UNALIGNEDBASE}${RUN} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/] >> ${PROJECTLOG}
rsync -r -t -e ssh ${UNALIGNEDBASE}${RUN} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/
rc=$?
NOW=$(date +"%Y%m%d%H%M%S")
if [[ ${rc} != 0 ]] ; then
  echo [${NOW}] [${RUN}] rsync to rasta failed: Error code: ${rc} >> ${PROJECTLOG}
else 
  echo [${NOW}] [${RUN}] scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN} >> ${PROJECTLOG}
  echo [${NOW}] [${RUN}] DEMUX transferred, script ends >> ${PROJECTLOG}
  scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}
fi
