#!/bin/bash

set -e
set -u

########
# VARS #
########

SCRIPT_DIR=$(dirname $(readlink -nm $0))
RAWBASE=/mnt/hds2/proj/bioinfo/Runs/
runs=$(ls $RAWBASE)

#############
# FUNCTIONS #
#############

function join { local IFS="$1"; shift; echo "$*"; }

########
# MAIN #
########

for run in ${runs[@]}; do
  NOW=$(date +"%Y%m%d%H%M%S")

  read -a RUN_PARTS <<< ${run}

  FC=$( echo ${run} | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')

  if [ -f ${RAWBASE}${run}/RTAComplete.txt ]; then
    if [ ! -f ${RAWBASE}${run}/demuxstarted.txt ]; then

        # process FCs serially
        FCS=( $(squeue --format=%j | grep Xdem | grep -v ${FC} | cut -d- -f 3 | sort | uniq) )
        if [[ ${#FCS[@]} > 0 ]]; then
            RUNNING_FCS=$(join , ${FCS[@]})
            echo [$NOW] ${run} ${RUNNING_FCS} are demuxing - Postpone demux!
            continue
        fi

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
