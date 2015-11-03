#!/bin/bash
#   usage:
#      xcreateunaligned.bash <absolute path to DEMUX Run folder>
#      Create the Unaligned/Project* folder structure like for an HiSeq2500 run.
#

VERSION=3.30.0

# DEMUX/RUN DIR
INDIR=$1

function join { local IFS="$1"; shift; echo "$*"; }

# determine some vars
BASENAME_INDIR=$(basename ${INDIR})
DATE=$(echo ${BASENAME_INDIR} | awk 'BEGIN {FS="_"} {print $1}')
FC=${BASENAME_INDIR: -9}

# read in the barcodes from the samplesheet
declare -A BARCODE_OF
while IFS=',' read -ra LINE; do
    if [[ ${#LINE[@]} -gt 2 ]]; then
        K=${LINE[2]}
        BARCODE_OF[$K]=${LINE[4]}
    fi
done < $INDIR/SampleSheet.csv

# easy way to check if we wrote meta data for a sample
# SAMPLE_PROJECT[${SANE_SAMPLE_ID}-${PROJECT_ID}]=1
declare -A SAMPLE_PROJECT

# Remove the previous links
rm -Rf ${INDIR}/Unaligned/

# link the fastq files and create the meta file
# loop over all projects
for PROJECT_DIR in $(find ${INDIR} -name 'Project_*' -exec basename {} \; | sort | uniq); do
    PROJECT_ID=${PROJECT_DIR##Project_}  # remove prefix Project_
    META_FILENAME=${OUTDIR}/${PROJECT_DIR}/${FC}/meta-${PROJECT_ID}-${FC}.txt 

    echo $PROJECT_DIR

    # loop over all samples of a project
    for SAMPLE_DIR in $(find ${INDIR}/*/${PROJECT_DIR}/ -name 'Sample_*' -exec basename {} \; | sort | uniq); do

        echo $SAMPLE_DIR

        SAMPLE_ID=${SAMPLE_DIR##Sample_} # remove prefix Sample_
        SANE_SAMPLE_ID=${SAMPLE_ID%%_*}  # remove all after _
        SAMPLE_BARCODE=${BARCODE_OF[${SAMPLE_ID}]} # get this sample's index

        mkdir -p ${INDIR}/Unaligned/${PROJECT_DIR}/${SAMPLE_DIR}/

        # loop over all fastq files of a sample
        for FASTQ_FILE_PATH in $(cd ${INDIR} && ls */${PROJECT_DIR}/${SAMPLE_DIR}/*.fastq.gz); do

            echo $FASTQ_FILE_PATH

            # BE AWARE
            # If a sample is in mulitple lanes, it will show up multiple times here!

            # 175984_S1_L002_R2_001.fastq.gz
            FASTQ_FILE=$(basename ${FASTQ_FILE_PATH})

            TILE=$(echo ${FASTQ_FILE_PATH} | awk 'BEGIN {FS="/"} {print $1}')
            FC_TILE=${FC}-${TILE} # make sure we won't overwrite fastq files from diff tiles

            # create a filename that's namespaced on FC, tile and included the barcode
            IFS='_' read -ra F_PARTS <<< "${FASTQ_FILE}" # split the fastq file name on '_'
            echo ${F_PARTS[@]}
            FASTQ_FILE_INDEX="${F_PARTS[0]}_${SAMPLE_BARCODE}_${F_PARTS[2]}_${F_PARTS[3]}_${F_PARTS[4]}"
            SAMPLE_FILE_NAME=${FC_TILE}_${FASTQ_FILE_INDEX}
            echo "ln-s ${INDIR}/${TILE}/${PROJECT_DIR}/${SAMPLE_DIR}/${FASTQ_FILE} ${INDIR}/Unaligned/${PROJECT_DIR}/${SAMPLE_DIR}/${SAMPLE_FILE_NAME}"
            
            # link
            #if [[ ! -e ${INDIR}/Unaligned/${PROJECT_DIR}/${SAMPLE_ID}/${SAMPLE_FILE_NAME} ]]; then
                ln -s ${INDIR}/${TILE}/${PROJECT_DIR}/${SAMPLE_DIR}/${FASTQ_FILE} ${INDIR}/Unaligned/${PROJECT_DIR}/${SAMPLE_DIR}/${SAMPLE_FILE_NAME}
            #fi
        done
    done

    # cp stats file
    #cp ${INDIR}/stats.txt ${OUTDIR}/${PROJECT_DIR}/${FC}/stats-${PROJECT_ID}-${FC}.txt
done
