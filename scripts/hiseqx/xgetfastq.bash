#!/bin/bash
#   usage:
#      xgetfastq.bash <absolute path to DEMUX Run folder>
#      Link from DEMUX to OUTBOX and rename fastq files to something more workable
# 

# DEMUX/RUN DIR
INDIR=$1 
OUTDIR=${2:-/mnt/hds/proj/bioinfo/OUTBOX/}
MIPDIR=${3:-/mnt/hds/proj/bioinfo/MIP_ANALYSIS/genomes/}

declare -A BARCODE_OF
while IFS=',' read -ra LINE; do
    if [[ ${#LINE[@]} -gt 2 ]]; then
        K=${LINE[2]}
        BARCODE_OF[$K]=${LINE[4]}
    fi
done < $INDIR/SampleSheet.csv

# second copy the actual fastq files
for TILE in `ls -d ${INDIR}/*/`; do
    TILE=$(echo ${TILE} | awk 'BEGIN {FS="/"} {print $(NF-1)}')
    for PROJECT_ID in `ls ${INDIR}/${TILE}`; do
        if [[ ${PROJECT_ID} == 'Reports' || ${PROJECT_ID} == 'Stats' ]]; then
            continue
        fi

        for SAMPLE_ID in `ls ${INDIR}/${TILE}/${PROJECT_ID}`; do
            for FASTQ_FILE in `ls ${INDIR}/${TILE}/${PROJECT_ID}/${SAMPLE_ID}/`; do
                if [[ ! -s ${INDIR}/${TILE}/${PROJECT_ID}/${SAMPLE_ID}/${FASTQ_FILE} ]]; then
                    continue
                fi

                SANE_SAMPLE_ID=${SAMPLE_ID//_/-}
                BASENAME_INDIR=$(basename ${INDIR})
                FC=${BASENAME_INDIR: -9}

                mkdir -p ${OUTDIR}/${PROJECT_ID}/${FC}/
                mkdir -p ${MIPDIR}/${SANE_SAMPLE_ID}/fastq/

                # 797220_S0_L004_R1_001.fastq.gz
                FASTQ_FILENAME=${FASTQ_FILE%%.*}
                DATE=$(echo ${BASENAME_INDIR} | awk 'BEGIN {FS="_"} {print $1}')
                FC_TILE=${FC}-${TILE:3:2}
                LANE=$(echo ${FASTQ_FILE} | awk '{split($(NF-1),arr,"_");print substr(arr[3],4,1)}')
                DIR=$(echo ${FASTQ_FILE} | awk '{split($(NF-1),arr,"_");print substr(arr[4],2,1)}')
                BC=${BARCODE_OF[${SAMPLE_ID}]}

                ln -s ${INDIR}/${TILE}/${PROJECT_ID}/${SAMPLE_ID}/${FASTQ_FILE} ${OUTDIR}/${PROJECT_ID}/${FC}/${LANE}_${DATE}_${FC_TILE}_${SANE_SAMPLE_ID}_${BC}_${DIR}.fastq.gz
                ln -s ${INDIR}/${TILE}/${PROJECT_ID}/${SAMPLE_ID}/${FASTQ_FILE} ${MIPDIR}/${SANE_SAMPLE_ID}/fastq/${LANE}_${DATE}_${FC_TILE}_${SANE_SAMPLE_ID}_${BC}_${DIR}.fastq.gz
            done
        done
    done
done
