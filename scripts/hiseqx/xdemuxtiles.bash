#!/bin/bash
# demux Xrun in parts

##########
# PARAMS #
##########

RUNDIR=$1 # full path to run dir
OUTDIR=/mnt/hds/proj/bioinfo/DEMUX/

#############
# FUNCTIONS #
#############

function join { local IFS="$1"; shift; echo "$*"; }

########
# MAIN #
########

NOW=$(date +"%Y%m%d%H%M%S")
SCRIPT_DIR=$(dirname $(readlink -nm $0))

if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
    echo ${RUNDIR}/SampleSheet.csv
    FC=$( basename `dirname ${RUNDIR}/SampleSheet.csv` | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
    echo [$NOW] wget http://tools.scilifelab.se/samplesheet/${FC}.csv
    wget http://tools.scilifelab.se/samplesheet/${FC}.csv -O ${RUNDIR}/${FC}.csv

    if [[ $? > 0 ]]; then
        echo [$NOW] wget FAILED with exit code: $?.
        exit
    fi

    # Downloaded samplesheet has following headers:
    #FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject

    # Needs to be changed to this:
    #[Data]
    #FCID,Lane,SampleID,SampleRef,Index,SampleName,Control,Recipe,Operator,Project

    echo '[Data]' > ${RUNDIR}/SampleSheet.csv
    sed  -e 's/Description/SampleName/' -e 's/SampleProject/Project/' ${RUNDIR}/${FC}.csv >> ${RUNDIR}/SampleSheet.csv
fi

echo "[${NOW}] starting overall process"
lanes=(1 2 3 4 5 6 7 8)
tiles=('11 12' '21 22')
DEMUX_JOBIDS=()
i=0
mkdir -p ${RUNDIR}/copycomplete/
for lane in "${lanes[@]}"; do
  for tile in "${tiles[@]}"; do
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] starting lane ${lane} tile ${tile}"
    RS=$(sbatch -J "Xdem-${lane}-${tile}" ${SCRIPT_DIR}/xdemuxtiles.batch ${RUNDIR} ${OUTDIR}/$(basename ${RUNDIR}) ${lane} ${tile})
    DEMUX_JOBIDS[$((i++))]=${RS##* }

    # Wait until the copy is complete ...
    tile_qs=( ${tile} )
    echo "${RUNDIR}/copycomplete/l${lane}t${tile_qs[0]}"
    while [[ ! -e ${RUNDIR}/copycomplete/l${lane}t${tile_qs[0]} ]]; do
        sleep 10
    done
  done
done

# launch the stats generation and linking after demux finishes ok
NOW=$(date +"%Y%m%d%H%M%S")
echo "[${NOW}] submit postface"
RUNNING_JOBIDS=( $(squeue -h --format=%i) ) # get all running/queued jobs
REMAINING_JOBIDS=( $(comm -12 <( printf '%s\n' "${RUNNING_JOBIDS[@]}" | LC_ALL=C sort ) <( printf '%s\n' "${DEMUX_JOBIDS[@]}" | LC_ALL=C sort )) ) # get all jobs that are still relevant
DEPENDENCY=""
if [[ ${#REMAINING_JOBIDS[@]} > 0 ]]; then
    DEPENDENCY="afterok:$(join : ${REMAINING_JOBIDS[@]})"
fi
echo "[${NOW}] Running ${RUNNING_JOBIDS[@]}"
echo "[${NOW}] Demux ${DEMUX_JOBIDS[@]}"
echo "[${NOW}] Remaining ${REMAINING_JOBIDS[@]}"
echo "[${NOW}] sbatch -A prod001 -t '00:01:00' --dependency=${DEPENDENCY} ${SCRIPT_DIR}/xpostface.batch ${OUTDIR}/$(basename ${RUNDIR})"
sbatch -J "Xdem-postface" --dependency=${DEPENDENCY} ${SCRIPT_DIR}/xpostface.batch ${OUTDIR}/$(basename ${RUNDIR})

###########
# CLEANUP #
###########

rm -Rf ${RUNDIR}/copycomplete/
rm -Rf ${RUNDIR}/copybackcomplete/
NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] everything started
