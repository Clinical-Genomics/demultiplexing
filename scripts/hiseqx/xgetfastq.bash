#!/bin/bash
#   usage:
#      xgetfastq.bash <absolute path to DEMUX Run folder>
#      Link from DEMUX to OUTBOX and rename fastq files to something more workable
#

# DEMUX/RUN DIR
INDIR=$1
OUTDIR=${2:-/mnt/hds/proj/bioinfo/OUTBOX/}
MIPDIR=${3:-/mnt/hds/proj/bioinfo/MIP_ANALYSIS/genomes/}

function join { local IFS="$1"; shift; echo "$*"; }

# read in the barcodes from the samplesheet
declare -A BARCODE_OF
while IFS=',' read -ra LINE; do
    if [[ ${#LINE[@]} -gt 2 ]]; then
        K=${LINE[2]}
        BARCODE_OF[$K]=${LINE[4]}
    fi
done < $INDIR/SampleSheet.csv

# determine some vars
BASENAME_INDIR=$(basename ${INDIR})
DATE=$(echo ${BASENAME_INDIR} | awk 'BEGIN {FS="_"} {print $1}')
FC=${BASENAME_INDIR: -9}

# easy way to check if we wrote meta data for a sample
# SAMPLE_PROJECT[${SANE_SAMPLE_ID}-${PROJECT_ID}]=1
declare -A SAMPLE_PROJECT

# reset previous linking and meta data creation
for TILE in `ls -d ${INDIR}/*/`; do
    TILE=$(basename ${TILE})
    for PROJECT_DIR in `ls ${INDIR}/${TILE}`; do
        if [[ ${PROJECT_DIR} == 'Reports' || ${PROJECT_DIR} == 'Stats' ]]; then
            continue
        fi

        echo "rm -Rf ${OUTDIR}/${PROJECT_DIR}/${FC}/"
        rm -Rf ${OUTDIR}/${PROJECT_DIR}/${FC}/
    done
done

# link the fastq files and create the meta file
# loop over all projects
for PROJECT_DIR in $(find ${INDIR} -name 'Project_*' -exec basename {} \; | uniq); do
    PROJECT_ID=${PROJECT_DIR##Project_}  # remove prefix Project_
    META_FILENAME=${OUTDIR}/${PROJECT_DIR}/${FC}/meta-${PROJECT_ID}-${FC}.txt 

    mkdir -p ${OUTDIR}/${PROJECT_DIR}/${FC}/

    # loop over all samples of a project
    for SAMPLE_DIR in $(find ${INDIR}/*/${PROJECT_DIR}/ -name 'Sample_*' -exec basename {} \; | uniq); do
        SAMPLE_ID=${SAMPLE_DIR##Sample_} # remove prefix Sample_
        BC=${BARCODE_OF[${SAMPLE_ID}]}   # look up the BarCode
        SANE_SAMPLE_ID=${SAMPLE_ID//_/-} # replace _ with -

        mkdir -p ${MIPDIR}/${SANE_SAMPLE_ID}/fastq/

        SAMPLE_FILE_NAMES=''
        # loop over all fastq files of a sample
        for FASTQ_FILE_PATH in $(cd ${INDIR} && ls */${PROJECT_DIR}/${SAMPLE_DIR}/*.fastq.gz); do
            FASTQ_FILE=$(basename ${FASTQ_FILE_PATH})
            FASTQ_SAMPLE_ID=$(echo ${FASTQ_FILE} | awk 'BEGIN {FS="_"} {print $1}')

            # Determine if this is an Undetermined index fastq file
            if [[ ${FASTQ_SAMPLE_ID} -eq ${PROJECT_ID} ]]; then
                FASTQ_SAMPLE_ID=${SANE_SAMPLE_ID}
            fi

            TILE=$(echo ${FASTQ_FILE_PATH} | awk 'BEGIN {FS="/"} {print $1}')
            DIR=$( echo ${FASTQ_FILE}      | awk 'BEGIN {FS="_"} {print substr($4,2,1)}')
            LANE=${TILE:1:1}
            FC_TILE=${FC}-${TILE:3:2} # make sure we won't overwrite fastq files from diff tiles

            SAMPLE_FILE_NAME=${LANE}_${DATE}_${FC_TILE}_${FASTQ_SAMPLE_ID}_${BC}_${DIR}.fastq.gz
            
            # link
            ln -s ${INDIR}/${TILE}/${PROJECT_DIR}/${SAMPLE_DIR}/${FASTQ_FILE} ${OUTDIR}/${PROJECT_DIR}/${FC}/${SAMPLE_FILE_NAME}
            ln -s ${INDIR}/${TILE}/${PROJECT_DIR}/${SAMPLE_DIR}/${FASTQ_FILE} ${MIPDIR}/${SANE_SAMPLE_ID}/fastq/${SAMPLE_FILE_NAME}

            # write the fastq file to the meta file
            SAMPLE_FILE_NAMES="${SAMPLE_FILE_NAMES}	${SAMPLE_FILE_NAME}"
        done

        # write out part of the meta file
        echo "${SANE_SAMPLE_ID}  ${FC}   ${LANE} ${BC}${SAMPLE_FILE_NAMES}" >> ${META_FILENAME}
    done

    # cp stats file
    cp ${INDIR}/stats.txt ${OUTDIR}/${PROJECT_DIR}/${FC}/stats.txt
done
