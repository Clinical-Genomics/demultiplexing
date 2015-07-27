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
BASENAME_INDIR=$(basename ${INDIR})
DATE=$(echo ${BASENAME_INDIR} | awk 'BEGIN {FS="_"} {print $1}')
FC=${BASENAME_INDIR: -9}
declare -A SAMPLE_PROJECT

for TILE in `ls -d ${INDIR}/*/`; do
    TILE=$(echo ${TILE} | awk 'BEGIN {FS="/"} {print $(NF-1)}')
    FC_TILE=${FC}-${TILE:3:2}
    for PROJECT_DIR in `ls ${INDIR}/${TILE}`; do
        if [[ ${PROJECT_DIR} == 'Reports' || ${PROJECT_DIR} == 'Stats' ]]; then
            continue
        fi

        PROJECT_ID=${PROJECT_DIR##Project_}

        for SAMPLE_ID in `ls ${INDIR}/${TILE}/${PROJECT_DIR}`; do
            SANE_SAMPLE_ID=${SAMPLE_ID##Sample_}
            BC=${BARCODE_OF[${SANE_SAMPLE_ID}]}
            SANE_SAMPLE_ID=${SANE_SAMPLE_ID//_/-}
            for FASTQ_FILE in `ls ${INDIR}/${TILE}/${PROJECT_DIR}/${SAMPLE_ID}/`; do
                if [[ ! -s ${INDIR}/${TILE}/${PROJECT_DIR}/${SAMPLE_ID}/${FASTQ_FILE} ]]; then
                    continue
                fi

                mkdir -p ${OUTDIR}/${PROJECT_DIR}/${FC}/
                mkdir -p ${MIPDIR}/${SANE_SAMPLE_ID}/fastq/

                # 797220_S0_L004_R1_001.fastq.gz
                LANE=$(echo ${FASTQ_FILE} | awk '{split($(NF-1),arr,"_");print substr(arr[3],4,1)}')
                DIR=$(echo ${FASTQ_FILE} | awk '{split($(NF-1),arr,"_");print substr(arr[4],2,1)}')
                SAMPLE_FILE_NAME=${LANE}_${DATE}_${FC_TILE}_${SANE_SAMPLE_ID}_${BC}_${DIR}.fastq.gz

                # link
                ln -s ${INDIR}/${TILE}/${PROJECT_DIR}/${SAMPLE_ID}/${FASTQ_FILE} ${OUTDIR}/${PROJECT_DIR}/${FC}/${SAMPLE_FILE_NAME}
                ln -s ${INDIR}/${TILE}/${PROJECT_DIR}/${SAMPLE_ID}/${FASTQ_FILE} ${MIPDIR}/${SANE_SAMPLE_ID}/fastq/${SAMPLE_FILE_NAME}
            done

            # write to meta file
            if [[ ${SAMPLE_PROJECT[${SANE_SAMPLE_ID}-${PROJECT_ID}]} -ne 1 ]]; then
                echo "${SANE_SAMPLE_ID}	${FC}	${LANE}	${BC}	${SAMPLE_FILE_NAME}	${SAMPLE_FILE_NAME%%_1.fastq.gz%_2.fastq.gz}" >> ${OUTDIR}/${PROJECT_DIR}/${FC}/meta-${PROJECT_ID}-${FC}.txt
                SAMPLE_PROJECT[${SANE_SAMPLE_ID}-${PROJECT_ID}]=1
            fi
        done

        # cp stats file
        cp ${INDIR}/stats.txt ${OUTDIR}/${PROJECT_DIR}/${FC}/stats.txt
    done
done
