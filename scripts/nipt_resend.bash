#!/bin/bash
# script to send run results

VERSION=3.39.5
echo "Version $VERSION"

##########
# PARAMS #
##########


RUN_DIR=$1
NIPTOUT=/srv/nipt_analysis_output/
NIPTCONF=/home/clinical/.niptrc
RUN=$(basename ${RUN_DIR})

if [[ -r $NIPTCONF ]]; then
    . $NIPTCONF
fi

#######
# RUN #
#######

INVESTIGATOR_NAME=$(sed 's//\n/g' ${RUN_DIR}/SampleSheet.csv  | grep 'Investigator Name' - | cut -d, -f2)
EXPERIMENT_NAME=$(sed 's//\n/g' ${RUN_DIR}/SampleSheet.csv  | grep 'Experiment Name' - | cut -d, -f2)
INVESTIGATOR_NAME=${INVESTIGATOR_NAME%$EXPERIMENT_NAME}
INVESTIGATOR_NAME=${INVESTIGATOR_NAME%_} # remove possible ending _

TMP_OUTDIR=`mktemp -d`

RESULTS_FILE_NAME=$(basename ${NIPTOUT}/{RUN}_*/*_NIPT_RESULTS.csv)
RESULTS_FILE_NAME="${INVESTIGATOR_NAME}_NIPT_RESULTS.csv"

OUTDIR=$(find ${NIPTOUT} -name "${RUN}_*" -type d)
cp ${OUTDIR}/*_NIPT_RESULTS.csv ${TMP_OUTDIR}/${RESULTS_FILE_NAME}

# FTP the results file
NOW=$(date +"%Y%m%d%H%M%S")
echo "lftp sftp://$NIPTSFTP_USER:$NIPTSFTP_PASSWORD@$NIPTSFTP_HOST -e 'cd SciLife_Till_StarLims; put ${TMP_OUTDIR}/${RESULTS_FILE_NAME}; bye'"
lftp sftp://$NIPTSFTP_USER:$NIPTSFTP_PASSWORD@$NIPTSFTP_HOST -e "cd SciLife_Till_StarLims; put ${TMP_OUTDIR}/${RESULTS_FILE_NAME}; bye"

rm -Rf ${TMP_OUTDIR}/${RESULTS_FILE_NAME}
rmdir ${TMP_OUTDIR}
