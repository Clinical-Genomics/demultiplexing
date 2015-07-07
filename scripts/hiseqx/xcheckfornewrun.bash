#!/bin/bash

SCRIPT_DIR=$(dirname $(readlink -nm $0))
RAWBASE=/mnt/hds2/proj/bioinfo/Runs/
runs=$(ls $RAWBASE)
for run in ${runs[@]}; do
  NOW=$(date +"%Y%m%d%H%M%S")
  if [ -f ${RAWBASE}${run}/RTAComplete.txt ]; then
    if [ ! -f ${RAWBASE}${run}/demuxstarted.txt ]; then
        echo [${NOW}] ${run} starting demultiplexing  
        date +'%Y%m%d%H%M%S' > ${RAWBASE}${run}/demuxstarted.txt
        ${SCRIPT_DIR}/xdemuxtiles.bash ${RAWBASE}${run}
    else 
      echo [${NOW}] ${run} is finished and demultiplexing has already started
    fi
  else
    echo [${NOW}] ${run} is not finished yet
  fi
done
