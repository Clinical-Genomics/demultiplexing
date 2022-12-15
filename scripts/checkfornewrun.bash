#!/bin/bash

shopt -s nullglob
shopt -s expand_aliases
source ~/.aliases

INDIR=${1?'please provide a run dur'}
DEMUXDIR=${2?'please provide a demux dir'}

CONDA_BASE="/home/proj/${ENVIRONMENT}/bin/miniconda3"
CONDA_EXE="${CONDA_BASE}/bin/conda"
CONDA_ENV_BASE="${CONDA_BASE}/envs"
CONDA_ENV="S_demux"

if [[ ${ENVIRONMENT} == 'production' ]]; then
    SLURM_ACCOUNT=production
    CONDA_ENV="P_demux"
fi

CONDA_RUN_COMMAND="${CONDA_EXE} run --name $CONDA_ENV ${CONDA_ENV_BASE}/${CONDA_ENV}/bin"

for RUNDIR in ${INDIR}/*; do
    RUN=$(basename ${RUNDIR})
    NOW=$(date +"%Y%m%d%H%M%S")
    if [[ -f ${RUNDIR}/RTAComplete.txt ]]; then
        if [[ ! -f ${RUNDIR}/demuxstarted.txt ]]; then
            if grep -qs '<Read Number="1" NumCycles="36" IsIndexedRead="N" />' ${RUNDIR}/runParameters.xml; then
                echo [${NOW}] ${RUN} is NIPT - skipping
                continue
            fi
            if [[ ! -e ${RUNDIR}/SampleSheet.ctmr ]]; then
                if grep -qs ',ctmr,' ${RUNDIR}/SampleSheet.csv; then
                    echo [${NOW}] ${RUN} is CTMR - transmogrifying SampleSheet.csv
                    cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/SampleSheet.ctmr
                    "${CONDA_RUN_COMMAND}/demux" sheet demux -a miseq ${RUNDIR}/SampleSheet.ctmr > ${RUNDIR}/SampleSheet.csv
                    cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/Data/Intensities/BaseCalls/
                fi
            fi
            if [[ ! -e ${RUNDIR}/SampleSheet.csv ]]; then
                echo [${NOW}] ${RUN} fetching samplesheet.csv
                FC=${RUN##*_}
                FC=${FC:1}
                "${CONDA_RUN_COMMAND}/demux" sheet fetch --application wes --shortest ${FC} > ${RUNDIR}/SampleSheet.csv
                cp ${RUNDIR}/SampleSheet.csv ${RUNDIR}/Data/Intensities/BaseCalls/
            fi
            echo [${NOW}] ${RUN} starting demultiplexing
            bash /home/hiseq.clinical/SCRIPTS/demux.bash ${RUNDIR} ${DEMUXDIR}
            rm ${DEMUXDIR}/copycomplete.txt
        else
            echo [${NOW}] ${RUN} is finished and demultiplexing has already started - started.txt exists
        fi
    else
        echo [${NOW}] ${RUN} is not finished yet
    fi
done
