#!/bin/bash
# demux Xrun in parts


shopt -s expand_aliases
source ~/.bashrc

set -eu -o pipefail


##########
# PARAMS #
##########

VERSION=4.26.4
RUNDIR=${1?'full path to run dir'}
OUTDIR=${2-/mnt/hds/proj/bioinfo/DEMUX/$(basename ${RUNDIR})/}


EMAIL=clinical-demux@scilifelab.se
LOGDIR="${OUTDIR}/LOG"
CP_COMPLETE_DIR=${OUTDIR}/copycomplete/ # dir to store cp-is-complete check file/lane-tile
SCRIPTDIR=$(dirname $(readlink -nm $0))

#############
# FUNCTIONS #
#############

join() { local IFS="$1"; shift; echo "$*"; }

log() {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo [${NOW}] $@
}

log_file() {
    NOW=$(date +"%Y%m%d%H%M%S")
    while read -r line; do
        L=$(echo $line | sed -e "s/^/[${NOW}] /")
        echo $L
    done < $1
}

failed() {
    PROJECTLOG=$(ls -tr1 ${OUTDIR}/projectlog.*.log | tail -1)
    cat ${PROJECTLOG} | mail -s "ERROR starting demux of $(basename $RUNDIR)" ${EMAIL}
}
trap failed ERR

########
# MAIN #
########

mkdir -p ${OUTDIR}
mkdir -p ${LOGDIR}
mkdir -p $CP_COMPLETE_DIR

log "demuxtiles.bash VERSION ${VERSION}"

# get the flowcell name
FC=$( basename $(basename ${RUNDIR}/) | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')

# is this a dual-index FC?
IS_DUAL=$(grep IndexRead2 ${RUNDIR}/runParameters.xml | sed 's/<\/IndexRead2>\r//' | sed 's/    <IndexRead2>//')

# get the samplesheet
if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
    DUALINDEX_PARAM=
    if [[ ${IS_DUAL} == '8' ]]; then
        DUALINDEX_PARAM='--dualindex'
    fi
    log "demux sheet fetch -a wgs ${DUALINDEX_PARAM} ${FC} > ${RUNDIR}/SampleSheet.csv"
    demux sheet fetch -a wgs ${DUALINDEX_PARAM} ${FC} > ${RUNDIR}/SampleSheet.csv
fi

# validate!
demux sheet validate --application wgs ${RUNDIR}/SampleSheet.csv

# notify we are ready to start!
cat ${RUNDIR}/SampleSheet.csv | mail -s "DEMUX of $FC started" ${EMAIL}

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
    JOB_TITLE="Xdem-l${lane}t${tile_qs[0]}-${FC}"
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
set +u # RUNNING_JOBIDS might be unbound
RUNNING_JOBIDS=( $(squeue -h --format=%i) ) # get all running/queued jobs
REMAINING_JOBIDS=( $(comm -12 <( printf '%s\n' "${RUNNING_JOBIDS[@]}" | LC_ALL=C sort ) <( printf '%s\n' "${DEMUX_JOBIDS[@]}" | LC_ALL=C sort )) ) # get all jobs that are still relevant
DEPENDENCY=""
if [[ ${#REMAINING_JOBIDS[@]} > 0 ]]; then
    DEPENDENCY="afterok:$(join : ${REMAINING_JOBIDS[@]})"
fi
log "Running ${RUNNING_JOBIDS[@]}"
log "Demux ${DEMUX_JOBIDS[@]}"
log "Remaining ${REMAINING_JOBIDS[@]}"
JOB_TITLE="xdem-xpostface-${FC}"
log "sbatch -J 'Xdem-postface' --dependency=${DEPENDENCY} -o ${LOGDIR}/${JOB_TITLE}-%j.log -e ${LOGDIR}/${JOB_TITLE}-%j.err ${SCRIPTDIR}/xpostface.batch ${OUTDIR}/"
     sbatch -J "Xdem-postface" --dependency=${DEPENDENCY} -o ${LOGDIR}/${JOB_TITLE}-%j.log -e ${LOGDIR}/${JOB_TITLE}-%j.err ${SCRIPTDIR}/xpostface.batch ${OUTDIR}/

###########
# CLEANUP #
###########

rm -Rf ${CP_COMPLETE_DIR}
log "Everything started"
