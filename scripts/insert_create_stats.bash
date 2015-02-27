#!/bin/bash
# USAGE: insert_create_stats.sh <RUNDIR>
# 
# When adding statistics to clinstatsdb fails, you can use this script to
# * add the statistics
# * create the stats-*.txt files
# * sync the stats-*.txt files to rasta

logfile=/home/clinical/LOG/demux.hiseq-clinical.log.txt
NOW=$(date +"%Y%m%d%H%M%S")
UNALIGNEDBASE=/home/clinical/DEMUX/
BACKUPDIR=/home/clinical/BACKUP/
BASE=$(echo $1 | awk '{if (substr($0,length($0),1) != "/") {print $0"/"} else {print $0}}')
RUN=$(echo ${BASE} | awk 'BEGIN {FS="/"} {print $(NF-1)}')
BASEMASKBYPASS=$2
PROJECTLOG=${UNALIGNEDBASE}${RUN}/projectlog.${NOW}.txt
NOW=$(date +"%Y%m%d%H%M%S")

# add to the DB
echo [${NOW}] [${RUN}] Demultiplexing finished,  adding stats to clinstatsdb . . . >> ${logfile}
echo [${NOW}] [${RUN}] Demultiplexing finished,  adding stats to clinstatsdb . . .  >> ${PROJECTLOG}
bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/parseunaligned_dbserver.py /home/clinical/DEMUX/${RUN}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv
echo [${NOW}] [${RUN}] bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/parseunaligned_dbserver.py >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] /home/clinical/DEMUX/${RUN}/ /home/clinical/RUNS/${RUN}/Data/Intensities/BaseCalls/SampleSheet.csv >> ${PROJECTLOG}

FC=$(echo ${BASE} | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
PROJs=$(ls ${UNALIGNEDBASE}${RUN}/Unaligned/ | grep Proj)
for PROJ in ${PROJs[@]};do
  prj=$(echo ${PROJ} | sed 's/Project_//')
  bash /home/clinical/SCRIPTS/rundbquery.bash /home/clinical/SCRIPTS/selectunaligned_dbserver.py ${prj} ${FC} > ${UNALIGNEDBASE}${RUN}/stats-${prj}-${FC}.txt
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
  echo [${NOW}] [${RUN}] scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN} >> ${PROJECTLOG}
  echo [${NOW}] [${RUN}] DEMUX transferred, script ends >> ${logfile}
  echo [${NOW}] [${RUN}] DEMUX transferred, script ends >> ${PROJECTLOG}
  scp ${PROJECTLOG} rastapopoulos.scilifelab.se:/mnt/hds/proj/bioinfo/DEMUX/${RUN}
fi
