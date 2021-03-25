#!/bin/bash
#SBATCH -c 18
#SBATCH --qos=high
#SBATCH --time=600
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=clinical-demux@scilifelab.se

set -eu -o pipefail

##########
# PARAMS #
##########

RUN_DIR=${1?'Run dir'}
DEMUX_DIR=${2?'Demux dir'}
UNALIGNED_DIR=${3?'Unaligned directory'}
EMAIL=clinical-demux@scilifelab.se

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
log "mkdir -p /home/proj/production/flowcells/novaseq/$SLURM_JOB_ID"
mkdir -p /home/proj/production/flowcells/novaseq/"$SLURM_JOB_ID"

################
# RUN BCL2FASTQ#
################

log "start demultiplexing ${RUN_DIR}"
log "singularity exec --bind /home/proj/production/demultiplexed-runs,/home/proj/production/flowcells/novaseq,/home/proj/production/flowcells/novaseq/"$SLURM_JOB_ID":/run/user/$(id -u) /home/proj/production/demux-on-hasta/novaseq/container/bcl2fastq_v2-20-0.sif bcl2fastq --loading-threads 3 --processing-threads 15 --writing-threads 3 --runfolder-dir ${RUN_DIR} --output-dir ${DEMUX_DIR}/${UNALIGNED_DIR} --sample-sheet ${RUN_DIR}/SampleSheet.csv --barcode-mismatches 1"
singularity exec --bind /home/proj/production/demultiplexed-runs,/home/proj/production/flowcells/novaseq,/home/proj/production/flowcells/novaseq/"$SLURM_JOB_ID":/run/user/$(id -u) /home/proj/production/demux-on-hasta/novaseq/container/bcl2fastq_v2-20-0.sif bcl2fastq --loading-threads 3 --processing-threads 15 --writing-threads 3 --runfolder-dir ${RUN_DIR} --output-dir ${DEMUX_DIR}/${UNALIGNED_DIR} --sample-sheet ${RUN_DIR}/SampleSheet.csv --barcode-mismatches 1
