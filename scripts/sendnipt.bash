#!/bin/bash
# script to send run results

VERSION=3.33.3
echo "Version $VERSION"

##########
# PARAMS #
##########

NIPTRUNS=/home/clinical/NIPT/
NIPTOUT=/srv/nipt_analysis_output/
MAILTO=kenny.billiau@scilifelab.se,emma.sernstad@scilifelab.se,daniel.backman@scilifelab.se,nipt@karolinska.se,valtteri.wirta@scilifelab.se

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
        RESULTS_FILE_NAME="${INVESTIGATOR_NAME}_${RESULTS_FILE_NAME}"

        # gather following files in a dir
        # tar them
        # mail!
        
        OUTDIR=`mktemp -d`
        
        cp -R ${NIPTRUNS}/${RUN}/InterOp ${OUTDIR}
        cp ${NIPTRUNS}/${RUN}/runParameters.xml ${OUTDIR}
        cp ${NIPTRUNS}/${RUN}/SampleSheet.csv ${OUTDIR}
        cp ${NIPTRUNS}/${RUN}/RunInfo.xml ${OUTDIR}
        cp ${NIPTOUT}/${RUN}_*/*_MISINDEXED_RESULTS.csv ${OUTDIR}
        cp ${NIPTOUT}/${RUN}_*/*_NIPT_RESULTS.csv ${OUTDIR}/${RESULTS_FILE_NAME}
        cp ${NIPTOUT}/${RUN}_*/REPORT.Complete.txt ${OUTDIR}
        
        SUBJECT="${INVESTIGATOR_NAME}_${EXPERIMENT_NAME}"
        RESULTS_FILE="results_${SUBJECT}.tgz"

        cd ${OUTDIR}
        tar -czf ${RESULTS_FILE} *
        cd -
        mail -s "Results ${SUBJECT}" -a ${OUTDIR}/${RESULTS_FILE} ${MAILTO} < ${NIPTOUT}/${RUN}_*/REPORT.Complete.txt 
        rm -Rf ${OUTDIR}

        date +'%Y%m%d%H%M%S' > ${NIPTRUNS}/${RUN}/delivery.txt
    fi
done
