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

if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
    echo >&2 "[$NOW] ${RUNDIR}/SampleSheet.csv not found! Aborting ..."
    exit 1
fi

echo "[${NOW}] starting overall process"
lanes=(1 2 3 4 5 6 7 8)
tiles=('11 12' '21 22')
mkdir -p ${RUNDIR}/copycomplete/
for lane in "${lanes[@]}"; do
  for tile in "${tiles[@]}"; do
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] starting lane ${lane} tile ${tile}"
    sbatch demuxtiles.batch $RUNDIR /mnt/hds2/proj/bioinfo/DEMUX/$(basename $RUNDIR) ${lane} ${tile}
    # Wait until the copy is complete ...
    tile_qs=( ${tile} )
    echo "${RUNDIR}/copycomplete/l${lane}t${tile_qs[0]}"
    while [[ ! -e ${RUNDIR}/copycomplete/l${lane}t${tile_qs[0]} ]]; do
        sleep 10 
    done
  done
done
rm ${RUNDIR}/copycomplete/*
NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] everything started
