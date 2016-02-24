#!/bin/bash
#   usage: demux.bash <absolute-path-to-run-dir>
#   The output i.e. Unaligned dir will be created 
#   under $UNALIGNEDBASE

VERSION=3.35.3

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
cp ${BASE}/SampleSheet.csv ${BASE}/SampleSheet.ori
grep -qs $'\r' ${BASE}/SampleSheet.csv
if [[ $? -eq 0 ]]; then
    sed -i 's//\n/g' ${BASE}/SampleSheet.csv
    cp ${BASE}/SampleSheet.csv ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv
fi

if [ ! -f ${BASE}Data/Intensities/BaseCalls/SampleSheet.csv ]; then 
  echo [${NOW}] [${RUN}] SampleSheet not found! Exits . . . >> ${logfile}
  echo [${NOW}] [${RUN}] SampleSheet not found! Exits . . . >> ${PROJECTLOG}
  exit
fi

echo [${NOW}] [${RUN}] Creating a demux SampleSheet ... >> ${logfile}
echo [${NOW}] [${RUN}] Creating a demux SampleSheet ... >> ${PROJECTLOG}
/home/clinical/SCRIPTS/massagenipt.py ${BASE}/SampleSheet.csv nuru > ${BASE}/SampleSheet.mas
mv ${BASE}/SampleSheet.mas ${BASE}/SampleSheet.csv
cp ${BASE}/SampleSheet.csv ${BASE}/Data/Intensities/BaseCalls/

NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] [${RUN}] Setup correct, starts demuxing . . . >> ${logfile}
echo [${NOW}] [${RUN}] Setup correct, starts demuxing . . . >> ${PROJECTLOG}

USEBASEMASK=Y36,I6n,Y36
UNALDIR=Unaligned

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

# copy the demultiplexed files to rasta
NOW=$(date +"%Y%m%d%H%M%S")
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
