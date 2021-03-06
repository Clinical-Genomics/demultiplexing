#!/bin/bash
#SBATCH -c 18
#SBATCH -p dragen # use this if you want to specify a partition to run test on, for instance `dragen` or `gpu`
#SBATCH --qos=low
#SBATCH --time=600
#SBATCH --mail-type=ALL
#SBATCH --mail-user=YOUR.NAME@scilifelab.se

set -eu -o pipefail

##########
# PARAMS #
##########

RUN_DIR=${1?'Run dir'}
DEMUX_DIR=${2?'Demux dir'}
BASEMASK=${3?'Basemask'}
UNALIGNED_DIR=${4?'Unaligned directory'}
EMAIL=YOUR.NAME@scilifelab.se

#############
# FUNCTIONS #
#############

log() {
    NOW=$(date +"%Y%m%d%H%M%S")
    echo "[${NOW}] $*"

}

failed() {
    mail -s "ERROR demultiplexing of $(basename "$RUN_DIR")" ${EMAIL} < "${DEMUX_DIR}/${UNALIGNED_DIR}/project.*.log"

}
trap failed ERR

########
# INIT #
########

log "On node: $(hostname)"
log "starting, will use ${TMPDIR}"
log "Run directory: ${RUN_DIR}"
log "Demux directory: ${DEMUX_DIR}"

#################
# RUN BCL2FASTQ #
#################

mkdir -p /home/proj/stage/flowcells/2500/"$SLURM_JOB_ID"
log "start demultiplexing ${RUN_DIR}"
log "singularity exec --bind /home/proj/stage/flowcells/2500,${DEMUX_DIR},/home/proj/stage/flowcells/2500/"$SLURM_JOB_ID":/run/user/$(id -u) /home/proj/stage/demux-on-hasta/novaseq/container/bcl2fastq_v2-20-0.sif bcl2fastq --loading-threads 3 --processing-threads 15 --writing-threads 3 --runfolder-dir ${RUN_DIR} --output-dir ${DEMUX_DIR}/${UNALIGNED_DIR} --use-bases-mask ${BASEMASK} --sample-sheet ${RUN_DIR}/SampleSheet.csv --barcode-mismatches 1 --ignore-missing-bcl"
singularity exec --bind /home/proj/stage/flowcells/2500,${DEMUX_DIR},/home/proj/stage/flowcells/2500/"$SLURM_JOB_ID":/run/user/$(id -u) /home/proj/stage/demux-on-hasta/novaseq/container/bcl2fastq_v2-20-0.sif bcl2fastq --loading-threads 3 --processing-threads 15 --writing-threads 3 --runfolder-dir ${RUN_DIR} --output-dir ${DEMUX_DIR}/${UNALIGNED_DIR} --use-bases-mask ${BASEMASK} --sample-sheet ${RUN_DIR}/SampleSheet.csv --barcode-mismatches 1 --ignore-missing-bcl
rm -rf /home/proj/stage/flowcells/2500/"$SLURM_JOB_ID"