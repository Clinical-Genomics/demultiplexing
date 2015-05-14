#!/bin/bash
# demux Xrun in parts

##########
# PARAMS #
##########

RUNDIR=$1
OUTDIR=/mnt/hds2/proj/bioinfo/TESTDEMUX/

########
# MAIN #
########

NOW=$(date +"%Y%m%d%H%M%S")

if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
    FC=$(echo ${RUNDIR} | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
    echo [$NOW] wget http://tools.scilifelab.se/samplesheet/${FC}.csv
    wget http://tools.scilifelab.se/samplesheet/${FC}.csv -O ${RUNDIR}/${FC}.csv

    # Downloaded samplesheet has following headers:
    #FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject

    # Needs to be changed to this:
    #[Data]
    #FCID,Lane,SampleID,SampleRef,Index,SampleName,Control,Recipe,Operator,Project

    echo '[Data]' > ${RUNDIR}/SampleSheet.csv
    sed  -e 's/Description/SampleName/' -e 's/SampleProject/Project/' ${RUNDIR}/${FC}.csv >> ${RUNDIR}/SampleSheet.csv
fi
exit

echo "[${NOW}] starting overall process"
lanes=(1 2 3 4 5 6 7 8)
tiles=('11 12' '21 22')
mkdir -p ${RUNDIR}/copycomplete/
for lane in "${lanes[@]}"; do
  for tile in "${tiles[@]}"; do
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] starting lane ${lane} tile ${tile}"
    sbatch demuxtiles.batch ${RUNDIR} ${OUTDIR}/$(basename ${RUNDIR}) ${lane} ${tile}
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
