#!/bin/bash
# demux Xrun in parts

##########
# PARAMS #
##########

RUNDIR=$1

########
# MAIN #
########

NOW=$(date +"%Y%m%d%H%M%S")
echo "[${NOW}] starting overall process"
lanes=(1 2 3 4 5 6 7 8)
tiles=('11 12' '21 22')
for lane in "${lanes[@]}"; do
  for tile in "${tiles[@]}"; do
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] starting lane ${lane} tile ${tile}"
    sbatch demuxtiles.batch $RUNDIR /mnt/hds2/proj/bioinfo/TESTDEMUX/$(basename $RUNDIR) ${lane} ${tile}
    # give the server some slack
    sleep 120 
  done
done
NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] everything started
