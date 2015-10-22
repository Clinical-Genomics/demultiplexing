#!/bin/bash
#   usage:
#      xcreateunaligned.bash <absolute path to DEMUX Run folder>
#      Create the Unaligned/Project* folder structure like for an HiSeq2500 run.
#

# DEMUX/RUN DIR
INDIR=$1

function join { local IFS="$1"; shift; echo "$*"; }

# determine some vars
BASENAME_INDIR=$(basename ${INDIR})
DATE=$(echo ${BASENAME_INDIR} | awk 'BEGIN {FS="_"} {print $1}')
FC=${BASENAME_INDIR: -9}

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

        mkdir -p ${INDIR}/Unaligned/${PROJECT_DIR}/${SAMPLE_ID}/

        # loop over all fastq files of a sample
        for FASTQ_FILE_PATH in $(cd ${INDIR} && ls */${PROJECT_DIR}/${SAMPLE_DIR}/*.fastq.gz); do

            echo $FASTQ_FILE_PATH

            # BE AWARE
            # If a sample is in mulitple lanes, it will show up multiple times here!

            FASTQ_FILE=$(basename ${FASTQ_FILE_PATH})

            TILE=$(echo ${FASTQ_FILE_PATH} | awk 'BEGIN {FS="/"} {print $1}')
            FC_TILE=${FC}-${TILE} # make sure we won't overwrite fastq files from diff tiles

            echo $TILE

            SAMPLE_FILE_NAME=${FC_TILE}_${FASTQ_FILE}
            
            # link
            #if [[ ! -e ${INDIR}/Unaligned/${PROJECT_DIR}/${SAMPLE_ID}/${SAMPLE_FILE_NAME} ]]; then
                ln -s ${INDIR}/${TILE}/${PROJECT_DIR}/${SAMPLE_DIR}/${FASTQ_FILE} ${INDIR}/Unaligned/${PROJECT_DIR}/${SAMPLE_ID}/${SAMPLE_FILE_NAME}
            #fi
        done
    done

    # cp stats file
    #cp ${INDIR}/stats.txt ${OUTDIR}/${PROJECT_DIR}/${FC}/stats-${PROJECT_ID}-${FC}.txt
done
