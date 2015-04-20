#!/bin/bash
# script to rsync a run to the NIPT server
# takes on argument: the rundir name

run=$1

RUNBASE=/home/clinical/RUNS/
NIPTBASE=/home/clinical/NIPT/

NIPTSERV=rastapopoulos.scilifelab.se
NIPTPATH=/mnt/hds2/proj/bioinfo/NIPT/

NOW=$(date +"%Y%m%d%H%M%S")
if [ -f ${RUNBASE}${run}/RTAComplete.txt ]; then
  if [ -e ${NIPTBASE}${run} ]; then
    echo [${NOW}] ${run} is finished and syncing has already started 
  else
    echo [${NOW}] ${run} is finished, starting syncing
    rsync -r -t --exclude RTAComplete.txt -e ssh ${RUNBASE}${run} ${NIPTSERV}:${NIPTPATH} && \
    scp ${RUNBASE}/$run ${NIPTSERV}:${NIPTPATH}/${run} && \
    ln -s ${RUNBASE}/${run} ${NIPTBASE}

    NOW=$(date +"%Y%m%d%H%M%S")
    if [[ $? == 0 ]]; then
    	echo [${NOW}] ${run} has finished syncing
    else
    	echo [${NOW}] ${run} has FAILED syncing
    fi
  fi
else
  echo [${NOW}] ${run} is not finished yet
fi
