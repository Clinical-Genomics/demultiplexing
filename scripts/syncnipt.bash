#!/bin/bash
# script to rsync a run to the NIPT server

VERSION=3.45.1
echo "Version $VERSION"

##########
# PARAMS #
##########

RUNBASE=/home/clinical/RUNS/
NIPTBASE=/home/clinical/NIPT/
NIPTOUTPATH=/home/clinical/tmp/
EMAILS=kenny.billiau@scilifelab.se

#######
# RUN #
#######

for RUN in ${RUNBASE}/*; do
  RUN=$(basename ${RUN})
  NOW=$(date +"%Y%m%d%H%M%S")
  if [[ ! -e ${NIPTBASE}${RUN} ]]; then
    # simple NIPT detection
    if grep -qs Description,cfDNAHiSeqv1.0 ${RUNBASE}${RUN}/SampleSheet.csv; then
      if [[ ! -e ${RUNBASE}${RUN}/SampleSheet.ori ]]; then
        cp ${RUNBASE}${RUN}/SampleSheet.csv ${RUNBASE}${RUN}/SampleSheet.ori
      fi

      # transform SampleSheet from Mac/Windows to Unix
      if grep -qs $'\r' ${RUNBASE}${RUN}/SampleSheet.csv; then
          sed -i 's//\n/g' ${RUNBASE}${RUN}/SampleSheet.csv
      fi
      sed -i '/^$/d' ${RUNBASE}${RUN}/SampleSheet.csv

      # validate
      if ! demux samplesheet validate ${RUNBASE}${RUN}/SampleSheet.csv; then
          NOW=$(date +"%Y%m%d%H%M%S")
          echo [${NOW}] ${RUN} has badly formatted SampleSheet!
          cat ${RUNBASE}${RUN}/SampleSheet.csv | mail -s "NIPT ${RUN} has a badly formatted SampleSheet!" $EMAILS
 
          continue
      fi

      # make SampleSheet NIPT ready
      demux samplesheet massage ${RUNBASE}${RUN}/SampleSheet.csv > ${RUNBASE}${RUN}/SampleSheet.mas
      mv ${RUNBASE}${RUN}/SampleSheet.mas ${RUNBASE}${RUN}/SampleSheet.csv
      cp ${RUNBASE}${RUN}/SampleSheet.csv ${RUNBASE}${RUN}/Data/Intensities/BaseCalls/

      # sync run to NIPT-TT server
      if [ -f ${RUNBASE}${RUN}/RTAComplete.txt ]; then
        echo [${NOW}] ${RUN} is finished, linking
        cp -al ${RUNBASE}${RUN} ${NIPTBASE}
        NOW=$(date +"%Y%m%d%H%M%S")
        echo [${NOW}] ${RUN} linking is finished, starting sync
        rsync -r --exclude RTAComplete.txt --exclude SampleSheet.csv --exclude Data/Intensities/BaseCalls/SampleSheet.csv ${NIPTBASE}${RUN} ${NIPTOUTPATH} && \
        cp ${NIPTBASE}/${RUN}/SampleSheet.csv ${NIPTOUTPATH}/${RUN}/
        cp ${NIPTBASE}/${RUN}/SampleSheet.csv ${NIPTOUTPATH}/${RUN}/Data/Intensities/BaseCalls/
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
