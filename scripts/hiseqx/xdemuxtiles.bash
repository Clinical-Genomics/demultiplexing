#!/bin/bash
# demux Xrun in parts

##########
# PARAMS #
##########

VERSION=3.34.0
RUNDIR=$1 # full path to run dir
OUTDIR=${2-/mnt/hds/proj/bioinfo/DEMUX/$(basename ${RUNDIR})/}
LOGDIR="${OUTDIR}/LOG"
CP_COMPLETE_DIR=${OUTDIR}/copycomplete/ # dir to store cp-is-complete check file/lane-tile
PROJECTLOG=${OUTDIR}/projectlog.$(date +'%Y%m%d%H%M%S').log

#############
# FUNCTIONS #
#############

join() { local IFS="$1"; shift; echo "$*"; }

log() {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo [${NOW}] $@
    echo [${NOW}] $@ >> ${PROJECTLOG}
}

log_file() {
    NOW=$(date +"%Y%m%d%H%M%S")
    while read -r line; do
        L=$(echo $line | sed -e "s/^/[${NOW}] /")
        echo $L
        echo $L >> ${PROJECTLOG}
    done < $1
}

########
# MAIN #
########

mkdir -p ${OUTDIR}
mkdir -p ${LOGDIR}
mkdir -p $CP_COMPLETE_DIR
SCRIPTDIR=$(dirname $(readlink -nm $0))

log "demuxtiles.bash VERSION ${VERSION}"

if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
    FC=$( basename `dirname ${RUNDIR}/SampleSheet.csv` | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
    log "wget http://tools.scilifelab.se/samplesheet/${FC}.csv"
    wget http://tools.scilifelab.se/samplesheet/${FC}.csv -O ${RUNDIR}/${FC}.csv

    if [[ $? > 0 ]]; then
        log "wget FAILED with exit code: $?."
        exit
    fi

    log "Downloaded sample sheet:"
    log_file ${RUNDIR}/${FC}.csv

    # Downloaded samplesheet has following headers:
    #FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject

    # Needs to be changed to this:
    #[Data]
    #FCID,Lane,SampleID,SampleRef,Index,SampleName,Control,Recipe,Operator,Project

    echo '[Data]' > ${RUNDIR}/SampleSheet.csv
    sed  -e 's/Description/SampleName/' -e 's/SampleProject/Project/' -e 's/Index/index/' -e 's/-[ACGT]*,/,/' ${RUNDIR}/${FC}.csv >> ${RUNDIR}/SampleSheet.csv
fi

log "Using sample sheet:"
log_file ${RUNDIR}/SampleSheet.csv

log "Starting overall process"
lanes=(1 2 3 4 5 6 7 8)
tiles=('11 12' '21 22')
DEMUX_JOBIDS=()
i=0
for lane in "${lanes[@]}"; do
  for tile in "${tiles[@]}"; do
    log "starting lane ${lane} tile ${tile}"

    tile_qs=( ${tile} )
    JOB_TITLE="Xdem-l${lane}t${tile_qs[0]}"
    log "sbatch -J $JOB_TITLE -o $LOGDIR/${JOB_TITLE}-%j.log -e ${LOGDIR}/${JOB_TITLE}-%j.err ${SCRIPTDIR}/xdemuxtiles.batch ${RUNDIR} ${OUTDIR}/ ${lane} ${tile}"
    RS=$(sbatch -J $JOB_TITLE -o $LOGDIR/${JOB_TITLE}-%j.log -e ${LOGDIR}/${JOB_TITLE}-%j.err ${SCRIPTDIR}/xdemuxtiles.batch ${RUNDIR} ${OUTDIR}/ ${lane} ${tile})
    DEMUX_JOBIDS[$((i++))]=${RS##* }

    log $RS

    # Wait until the copy is complete ...
    while [[ ! -e ${CP_COMPLETE_DIR}/l${lane}t${tile_qs[0]} ]]; do
        sleep 10
    done
  done
done

# launch the stats generation and linking after demux finishes ok
log "submit postface"
RUNNING_JOBIDS=( $(squeue -h --format=%i) ) # get all running/queued jobs
REMAINING_JOBIDS=( $(comm -12 <( printf '%s\n' "${RUNNING_JOBIDS[@]}" | LC_ALL=C sort ) <( printf '%s\n' "${DEMUX_JOBIDS[@]}" | LC_ALL=C sort )) ) # get all jobs that are still relevant
DEPENDENCY=""
if [[ ${#REMAINING_JOBIDS[@]} > 0 ]]; then
    DEPENDENCY="afterok:$(join : ${REMAINING_JOBIDS[@]})"
fi
log "Running ${RUNNING_JOBIDS[@]}"
log "Demux ${DEMUX_JOBIDS[@]}"
log "Remaining ${REMAINING_JOBIDS[@]}"
JOB_TITLE="xdem-xpostface"
log "sbatch -J 'Xdem-postface' --dependency=${DEPENDENCY} -o ${LOGDIR}/${JOB_TITLE}-%j.log -e ${LOGDIR}/${JOB_TITLE}-%j.err ${SCRIPTDIR}/xpostface.batch ${OUTDIR}/"
sbatch -J "Xdem-postface" --dependency=${DEPENDENCY} -o ${LOGDIR}/${JOB_TITLE}-%j.log -e ${LOGDIR}/${JOB_TITLE}-%j.err ${SCRIPTDIR}/xpostface.batch ${OUTDIR}/

###########
# CLEANUP #
###########

rm -Rf ${CP_COMPLETE_DIR}
log "Everything started"
