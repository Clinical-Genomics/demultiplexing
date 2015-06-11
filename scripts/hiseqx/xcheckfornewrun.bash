#!/bin/bash

RAWBASE=/mnt/hds2/proj/bioinfo/Runs/
runs=$(ls $RAWBASE)
for run in ${runs[@]}; do
  NOW=$(date +"%Y%m%d%H%M%S")
  if [ -f ${RAWBASE}${run}/RTAComplete.txt ]; then
    if [ ! -f ${RAWBASE}${run}/demuxstarted.txt ]; then
        echo [${NOW}] ${run} starting demultiplexing  
        date +'%Y%m%d%H%M%S' > ${RAWBASE}${run}/demuxstarted.txt
        /mnt/hds/proj/bioinfo/SCRIPTS/xdemuxtiles.bash ${RAWBASE}${run} &
    else 
      echo [${NOW}] ${run} is finished and demultiplexing has already started - started.txt exists
    fi
  else
    echo [${NOW}] ${run} is not finished yet
  fi
done
