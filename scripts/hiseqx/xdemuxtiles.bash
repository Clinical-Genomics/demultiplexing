#!/bin/bash
# demux Xrun in parts

##########
# PARAMS #
##########

VERSION=3.16.4
RUNDIR=$1 # full path to run dir
OUTDIR="/mnt/hds/proj/bioinfo/DEMUX/$(basename ${RUNDIR})"
CP_COMPLETE_DIR=${OUTDIR}/copycomplete/ # dir to store cp-is-complete check file/lane-tile

#############
# FUNCTIONS #
#############

function join { local IFS="$1"; shift; echo "$*"; }

########
# MAIN #
########

mkdir -p ${OUTDIR}
mkdir -p $CP_COMPLETE_DIR
SCRIPT_DIR=$(dirname $(readlink -nm $0))
PROJECTLOG=${OUTDIR}/projectlog.$(date +'%Y%m%d%H%M%S').log

NOW=$(date +"%Y%m%d%H%M%S")
echo "[${NOW}] VERSION ${VERSION}" >> ${PROJECTLOG}

if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
    FC=$( basename `dirname ${RUNDIR}/SampleSheet.csv` | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
    echo [$NOW] wget http://tools.scilifelab.se/samplesheet/${FC}.csv >> ${PROJECTLOG}
    wget http://tools.scilifelab.se/samplesheet/${FC}.csv -O ${RUNDIR}/${FC}.csv

    if [[ $? > 0 ]]; then
        echo [$NOW] wget FAILED with exit code: $?. >> ${PROJECTLOG}
        exit
    fi

    # Downloaded samplesheet has following headers:
    #FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject

    # Needs to be changed to this:
    #[Data]
    #FCID,Lane,SampleID,SampleRef,Index,SampleName,Control,Recipe,Operator,Project

    echo '[Data]' > ${RUNDIR}/SampleSheet.csv
    sed  -e 's/Description/SampleName/' -e 's/SampleProject/Project/' -e 's/Index/index/' -e 's/-[ACGT]*,/,/' ${RUNDIR}/${FC}.csv >> ${RUNDIR}/SampleSheet.csv
    exit
fi

cat ${RUNDIR}/SampleSheet.csv >> ${PROJECTLOG}

echo "[${NOW}] starting overall process" >> ${PROJECTLOG}
lanes=(1 2 3 4 5 6 7 8)
tiles=('11 12' '21 22')
DEMUX_JOBIDS=()
i=0
for lane in "${lanes[@]}"; do
  for tile in "${tiles[@]}"; do
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] starting lane ${lane} tile ${tile}" >> ${PROJECTLOG}
    RS=$(sbatch -J "Xdem-${lane}-${tile}" ${SCRIPT_DIR}/xdemuxtiles.batch ${RUNDIR} ${OUTDIR}/ ${lane} ${tile})
    DEMUX_JOBIDS[$((i++))]=${RS##* }

    # Wait until the copy is complete ...
    tile_qs=( ${tile} )
    while [[ ! -e ${CP_COMPLETE_DIR}/l${lane}t${tile_qs[0]} ]]; do
        sleep 10
    done
  done
done

# launch the stats generation and linking after demux finishes ok
NOW=$(date +"%Y%m%d%H%M%S")
echo "[${NOW}] submit postface" >> ${PROJECTLOG}
RUNNING_JOBIDS=( $(squeue -h --format=%i) ) # get all running/queued jobs
REMAINING_JOBIDS=( $(comm -12 <( printf '%s\n' "${RUNNING_JOBIDS[@]}" | LC_ALL=C sort ) <( printf '%s\n' "${DEMUX_JOBIDS[@]}" | LC_ALL=C sort )) ) # get all jobs that are still relevant
DEPENDENCY=""
if [[ ${#REMAINING_JOBIDS[@]} > 0 ]]; then
    DEPENDENCY="afterok:$(join : ${REMAINING_JOBIDS[@]})"
fi
echo "[${NOW}] Running ${RUNNING_JOBIDS[@]}" >> ${PROJECTLOG}
echo "[${NOW}] Demux ${DEMUX_JOBIDS[@]}" >> ${PROJECTLOG}
echo "[${NOW}] Remaining ${REMAINING_JOBIDS[@]}" >> ${PROJECTLOG}
echo "[${NOW}] sbatch -A prod001 -t '00:01:00' --dependency=${DEPENDENCY} ${SCRIPT_DIR}/xpostface.batch ${OUTDIR}/" >> ${PROJECTLOG}
sbatch -J "Xdem-postface" --dependency=${DEPENDENCY} ${SCRIPT_DIR}/xpostface.batch ${OUTDIR}/

###########
# CLEANUP #
###########

rm -Rf ${CP_COMPLETE_DIR}
NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] Everything started >> ${PROJECTLOG}
