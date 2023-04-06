#!/bin/bash
# demux Xrun in parts

set -eu -o pipefail
shopt -s expand_aliases

##########
# PARAMS #
##########

VERSION=5.11.1
RUNDIR=${1?'full path to run dir'}
OUTDIR=${2-"/home/proj/${ENVIRONMENT}/demultiplexed-runs/$(basename "${RUNDIR}")/"}

EMAIL=clinical-demux@scilifelab.se
LOGDIR="${OUTDIR}/LOG"
SCRIPTDIR="$(dirname "$(readlink -nm "$0")")"

if [[ ${ENVIRONMENT} == 'production' ]]; then
    useprod
    SLURM_ACCOUNT=production
elif [[ ${ENVIRONMENT} == 'stage' ]]; then
    usestage
    SLURM_ACCOUNT=development
fi

#############
# FUNCTIONS #
#############

join() { local IFS="$1"; shift; echo "$*"; }

log() {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] $*"
}

log_file() {
    NOW=$(date +"%Y%m%d%H%M%S")
    while read -r line; do
        L=${line//[${NOW}] }
        echo "$L"
    done < "$1"
}

failed() {
    PROJECTLOG=$(ls -tr1 "${OUTDIR}/projectlog.*.log" | tail -1)
    mail -s "ERROR starting demux of $(basename "$RUNDIR")" ${EMAIL} < "${PROJECTLOG}"
}
trap failed ERR

########
# MAIN #
########

mkdir -p "${OUTDIR}"
mkdir -p "${LOGDIR}"

log "demuxtiles.bash VERSION ${VERSION}"

# get the flowcell name
FC=$(basename "$(basename "${RUNDIR}"/)" | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')

# is this a dual-index FC?
IS_DUAL=$(grep IndexRead2 "${RUNDIR}/runParameters.xml" | sed 's/<\/IndexRead2>\r//' | sed 's/    <IndexRead2>//')

# calculate the number of lanes
LANE_COUNT=$(awk '$0 ~/FlowcellLayout/ {split($0,arr," "); split(arr[2],o,"="); print o[2]}' "${RUNDIR}/RunInfo.xml" | sed 's/\"//g')
declare -a lanes=()
for (( i=1; i<=LANE_COUNT; i++ )); do
  lanes[$i-1]=$i;
done

# get the samplesheet
if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
    DUALINDEX_PARAM=
    if [[ ${IS_DUAL} == '8' ]]; then
        DUALINDEX_PARAM='--dualindex'
    fi
    log "demux sheet fetch -a wgs ${DUALINDEX_PARAM} ${FC} > ${RUNDIR}/SampleSheet.csv"
    demux sheet fetch -a wgs $DUALINDEX_PARAM "${FC}" > "${RUNDIR}/SampleSheet.csv"
fi

# validate!
log "demux sheet validate --application wgs "${RUNDIR}/SampleSheet.csv""
demux sheet validate --application wgs "${RUNDIR}/SampleSheet.csv"

# notify we are ready to start!
mail -s "DEMUX of $FC started" ${EMAIL} < "${RUNDIR}/SampleSheet.csv"

log "Using sample sheet:"
log_file "${RUNDIR}/SampleSheet.csv"

log "Starting overall process"
tiles=('11 12' '21 22')
DEMUX_JOBIDS=()
i=0
for lane in "${lanes[@]}"; do
  for tile in "${tiles[@]}"; do
    log "starting lane ${lane} tile ${tile}"

    tile_qs=( ${tile} )
    JOB_TITLE="Xdem-l${lane}t${tile_qs[0]}-${FC}"
    log "sbatch -A ${SLURM_ACCOUNT} -J '$JOB_TITLE' -o '$LOGDIR/${JOB_TITLE}-%j.log' -e '${LOGDIR}/${JOB_TITLE}-%j.err' '${SCRIPTDIR}/xdemuxtiles.batch' '${RUNDIR}' '${OUTDIR}/' '${lane}' '${ENVIRONMENT}' '${tile}'"
    RS=$(sbatch -A ${SLURM_ACCOUNT} -J "$JOB_TITLE" -o "$LOGDIR/${JOB_TITLE}-%j.log" -e "${LOGDIR}/${JOB_TITLE}-%j.err" "${SCRIPTDIR}/xdemuxtiles.batch" "${RUNDIR}" "${OUTDIR}/" "${lane}" "${ENVIRONMENT}" "${tile}")
    DEMUX_JOBIDS[$((i++))]=${RS##* }

    log "$RS"
  done
done

# launch the stats generation and linking after demux finishes ok
log "submit postface"
set +u # RUNNING_JOBIDS might be unbound
RUNNING_JOBIDS=( $(squeue -h --format=%i) ) # get all running/queued jobs
REMAINING_JOBIDS=( $(comm -12 <( printf '%s\n' "${RUNNING_JOBIDS[@]}" | LC_ALL=C sort ) <( printf '%s\n' "${DEMUX_JOBIDS[@]}" | LC_ALL=C sort )) ) # get all jobs that are still relevant
DEPENDENCY=""
if [[ ${#REMAINING_JOBIDS[@]} -gt 0 ]]; then
    DEPENDENCY="afterok:$(join : "${REMAINING_JOBIDS[@]}")"
fi
log "Running ${RUNNING_JOBIDS[*]}"
log "Demux ${DEMUX_JOBIDS[*]}"
log "Remaining ${REMAINING_JOBIDS[*]}"
JOB_TITLE="xdem-xpostface-${FC}"
log "sbatch -A ${SLURM_ACCOUNT} -J 'Xdem-postface' --dependency='${DEPENDENCY}' -o '${LOGDIR}/${JOB_TITLE}-%j.log' -e '${LOGDIR}/${JOB_TITLE}-%j.err' '${SCRIPTDIR}/xpostface.batch' '${OUTDIR}/'"
     sbatch -A ${SLURM_ACCOUNT} -J "Xdem-postface" --dependency="${DEPENDENCY}" -o "${LOGDIR}/${JOB_TITLE}-%j.log" -e "${LOGDIR}/${JOB_TITLE}-%j.err" "${SCRIPTDIR}/xpostface.batch" "${OUTDIR}/"

###########
# CLEANUP #
###########

log "Everything started"
