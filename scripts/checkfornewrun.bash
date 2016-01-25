#!/bin/bash
#
RAWBASE=/home/clinical/RUNS/
UNABASE=/home/clinical/DEMUX/
runs=$(ls /home/clinical/RUNS/)
for run in ${runs[@]}; do
  NOW=$(date +"%Y%m%d%H%M%S")
  if [ -f ${RAWBASE}${run}/RTAComplete.txt ]; then
    if [ -d ${UNABASE}${run}/Unaligned ]; then
      echo [${NOW}] ${run} is finished and demultiplexing has already started - Unaligned exists
    else
      if [ ! -f ${UNABASE}${run}/started.txt ]; then
        echo [${NOW}] ${run} is finished but demultiplexing has not started
        demuxproccount=$(ps aux | grep HISEQ | grep grep -v | wc | awk '{print $1}')
        if [[ "${demuxproccount}" -lt 15 ]]; then
          echo [${NOW}] ${run} starting demultiplexing  
          bash /home/clinical/SCRIPTS/demux.v5.bash ${RAWBASE}${run} &
        else  
          echo [${NOW}] ${run} did not start demultiplexing other processes running
        fi
      else 
        echo [${NOW}] ${run} is finished and demultiplexing has already started - started.txt exists
      fi
    fi
  else
    echo [${NOW}] ${run} is not finished yet
  fi
done
