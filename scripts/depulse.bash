#!/bin/bash
# create one fastq file from several from a pulsed run.

# * loop over all unaligned.
# * loop over all projects.
# * cat 1 file / readdirection, 1 file for each lane.
# * move old files out of the way.

DEMUX_DIR=$1

[[ -z ${DEMUX_DIR} ]] && echo "USAGE: $0 <path to demux run dir>" && exit 1

for UNALIGN_DIR in ${DEMUX_DIR}/Unaligned*; do
    for PROJECT_DIR in ${UNALIGN_DIR}/Project_*; do
        for SAMPLE_DIR in ${PROJECT_DIR}/Sample_*; do
            mkdir ${SAMPLE_DIR}/Merged
            mkdir ${SAMPLE_DIR}/Original

            for READ_DIR in 1 2; do
                for LANE in $( cd ${SAMPLE_DIR} && ls *_L*fastq.gz | awk -F '_' '{ print $4 }' | sort | uniq ); do
                    OUTPUT_FILENAME=$( cd ${SAMPLE_DIR} && ls *_${LANE}_R${READ_DIR}_001* )

                    echo "cat ${SAMPLE_DIR}/*_${LANE}_R${READ_DIR}_* > ${SAMPLE_DIR}/Merged/${OUTPUT_FILENAME}"
                    cat ${SAMPLE_DIR}/*_${LANE}_R${READ_DIR}_* > ${SAMPLE_DIR}/Merged/${OUTPUT_FILENAME}

                    echo "mv ${SAMPLE_DIR}/*_${LANE}_R${READ_DIR}_* ${SAMPLE_DIR}/Original/"
                    mv ${SAMPLE_DIR}/*_${LANE}_R${READ_DIR}_* ${SAMPLE_DIR}/Original/
                done
            done

            echo "mv ${SAMPLE_DIR}/Merged/* ${SAMPLE_DIR}"
            mv ${SAMPLE_DIR}/Merged/* ${SAMPLE_DIR}

            echo "rmdir ${SAMPLE_DIR}/Merged/"
            rmdir ${SAMPLE_DIR}/Merged/
        done
    done
done
