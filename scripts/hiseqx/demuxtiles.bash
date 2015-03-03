#!/bin/bash
# demux Xrun in parts

##########
# PARAMS #
##########

RUNNAME=$1

########
# MAIN #
########

NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] starting overall process
lanes=(1 2 3 4 5 6 7 8)
quarts=('11 12' '21 22')
for lane in "${lanes[@]}"; do
  for quart in "${quarts[@]}"; do
    NOW=$(date +"%Y%m%d%H%M%S")
    echo [${NOW}] starting lane${lane}_${quart}
    #echo "sbatch demuxtiles.batch $RUNNAME /mnt/hds2/proj/bioinfo/DEMUX/$(basename $RUNNAME) ${lane} ${quart}"
    sbatch demuxtiles.batch $RUNNAME /mnt/hds/proj/bioinfo/tmp/X/$(basename $RUNNAME) ${lane} ${quart}
    # wait a minute so copying doesn't slow the server
    sleep 60 
  done
done
NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] everything started
