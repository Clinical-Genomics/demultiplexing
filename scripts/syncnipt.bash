#!/bin/bash
# script to rsync a run to the NIPT server

VERSION=3.9.0

RUNBASE=/home/clinical/RUNS/
NIPTBASE=/home/clinical/NIPT/
NIPTOUTPATH=/srv/nipt_runs/

NOW=$(date +"%Y%m%d%H%M%S")
RUNS=$(ls ${RUNBASE})

for RUN in ${RUNS[@]}; do
  if [[ ! -e ${NIPTBASE}${RUN} ]]; then
    # simple NIPT detection
    grep -qs Description,NIPTv1 ${RUNBASE}${RUN}/SampleSheet.csv
    if [[ $? -eq 0 ]]; then
      if [ -f ${RUNBASE}${RUN}/RTAComplete.txt ]; then
        echo [${NOW}] ${RUN} is finished, linking
        cp -al ${RUNBASE}${RUN} ${NIPTBASE}
        NOW=$(date +"%Y%m%d%H%M%S")
        echo [${NOW}] ${RUN} linking is finished, starting sync
        rsync -r --exclude RTAComplete.txt ${NIPTBASE}${RUN} ${NIPTOUTPATH} && \
        cp ${NIPTBASE}/${RUN}/RTAComplete.txt ${NIPTOUTPATH}/${RUN}/
    
        if [[ $? == 0 ]]; then
          NOW=$(date +"%Y%m%d%H%M%S")
          echo [${NOW}] ${RUN} has finished syncing
        else
          NOW=$(date +"%Y%m%d%H%M%S")
          echo [${NOW}] ${RUN} has FAILED syncing
        fi
      else
        echo [${NOW}] ${RUN} is not finished yet
      fi
    else
      NOW=$(date +"%Y%m%d%H%M%S")
      echo [$NOW] ${RUN} is not a NIPT run!
    fi
  else
    NOW=$(date +"%Y%m%d%H%M%S")
    echo [$NOW] ${RUN} has already synced
  fi
done
