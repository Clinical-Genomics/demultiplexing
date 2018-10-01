#!/bin/bash
# script to send run results

set -ue

VERSION=4.23.0
echo "Version $VERSION"

##########
# PARAMS #
##########

NIPTRUNS=/home/hiseq.clinical/NIPT/
NIPTOUT=/srv/nipt_analysis_output/
MAILTO=clinical-demux@scilifelab.se,nipt.karolinska@sll.se
MAILTO_RERUN=agne.lieden@ki.se,kenny.billiau@scilifelab.se
MAILTO_ERR=clinical-demux@scilifelab.se
NIPTCONF=/home/hiseq.clinical/.niptrc

if [[ -r $NIPTCONF ]]; then
    . $NIPTCONF
else
    echo "NIPT config not found!" | mail -s "NIPT config not found on $(hostname)" ${MAILTO_ERR}
fi

#############
# FUNCTIONS #
#############

failed() {
    echo "Fail to send ${RUN}. Error on line nr: $(caller)" | mail -s "ERROR sending NIPT $(hostname):${RUN}" ${MAILTO_ERR}
}
trap failed ERR

#######
# RUN #
#######

for RUN in $(ls ${NIPTRUNS}); do
    NOW=$(date +"%Y%m%d%H%M%S")
    if [[ ${RUN} =~ 'TEST' ]]; then
        echo [${NOW}] [${RUN}] TEST run, skipping ...
        continue # skip test runs
    fi
    echo [${NOW}] [${RUN}] Checking ...
    if [[ -e ${NIPTRUNS}/${RUN}/delivery.txt ]]; then
        while read line; do echo [${NOW}] [${RUN}] Delivered on $line; done < ${NIPTRUNS}/${RUN}/delivery.txt
        continue
    fi

    OUTDIR=$(find ${NIPTOUT} -name "${RUN}_*" -type d)
    if [[ ! -d ${OUTDIR} ]]; then
        echo [${NOW}] [${RUN}] Not finished yet ...
    else
        echo [${NOW}] [${RUN}] Mailing!

        INVESTIGATOR_NAME=$(sed 's//\n/g' ${NIPTRUNS}/${RUN}/SampleSheet.csv  | grep 'Investigator Name' - | cut -d, -f2)
        EXPERIMENT_NAME=$(sed 's//\n/g' ${NIPTRUNS}/${RUN}/SampleSheet.csv  | grep 'Experiment Name' - | cut -d, -f2)
        INVESTIGATOR_NAME=${INVESTIGATOR_NAME%$EXPERIMENT_NAME}
        INVESTIGATOR_NAME=${INVESTIGATOR_NAME%_} # remove possible ending _

        RESULTS_FILE_NAME=$(basename ${NIPTOUT}/${RUN}_*/*_NIPT_RESULTS.csv)
        RESULTS_FILE_NAME="${INVESTIGATOR_NAME}_NIPT_RESULTS.csv"

        # gather following files in a dir
        # tar them
        # mail!
        
        TMP_OUTDIR=`mktemp -d`
        
        cp -R ${NIPTRUNS}/${RUN}/InterOp ${TMP_OUTDIR}
        cp ${NIPTRUNS}/${RUN}/runParameters.xml ${TMP_OUTDIR}
        cp ${NIPTRUNS}/${RUN}/SampleSheet.csv ${TMP_OUTDIR}
        cp ${NIPTRUNS}/${RUN}/RunInfo.xml ${TMP_OUTDIR}
        cp ${OUTDIR}/*_MISINDEXED_RESULTS.csv ${TMP_OUTDIR}
        cp ${OUTDIR}/*_NIPT_RESULTS.csv ${TMP_OUTDIR}/${RESULTS_FILE_NAME}
        cp ${OUTDIR}/REPORT.Complete.txt ${TMP_OUTDIR}

        SUBJECT="${INVESTIGATOR_NAME}_${EXPERIMENT_NAME}"
        RESULTS_FILE="results_${SUBJECT}.tgz"

        cd ${TMP_OUTDIR}
        tar -czf ${RESULTS_FILE} *
        cd -

        IFS=_ read -ra RUN_PARTS <<< "${RUN}"
        unset IFS
        DATE=${RUN_PARTS[0]}
        if [[ $DATE > 161121 ]]; then
            mail -s "Results ${SUBJECT}" -a ${TMP_OUTDIR}/${RESULTS_FILE} ${MAILTO} < ${NIPTOUT}/${RUN}_*/REPORT.Complete.txt 
            # FTP the results file
            NOW=$(date +"%Y%m%d%H%M%S")
            lftp sftp://$NIPTSFTP_USER:$NIPTSFTP_PASSWORD@$NIPTSFTP_HOST -e "cd SciLife_Till_StarLims; put ${TMP_OUTDIR}/${RESULTS_FILE_NAME}; bye"
        else
            mail -s "Results ${SUBJECT}" -a ${TMP_OUTDIR}/${RESULTS_FILE} ${MAILTO_RERUN} < ${NIPTOUT}/${RUN}_*/REPORT.Complete.txt 
        fi

        # clean up
        echo "rm -Rf ${TMP_OUTDIR}"
        rm -Rf ${TMP_OUTDIR}

        date +'%Y%m%d%H%M%S' > ${NIPTRUNS}/${RUN}/delivery.txt
    fi
done
