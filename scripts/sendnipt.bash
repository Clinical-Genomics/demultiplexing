#!/bin/bash
# script to send run results

VERSION=3.30.2
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
        # gather following files in a dir
        # tar them
        # mail!
        
        OUTDIR=`mktemp -d`
        
        cp -R ${NIPTRUNS}/${RUN}/InterOp ${OUTDIR}
        cp ${NIPTRUNS}/${RUN}/runParameters.xml ${OUTDIR}
        cp ${NIPTRUNS}/${RUN}/SampleSheet.csv ${OUTDIR}
        cp ${NIPTRUNS}/${RUN}/RunInfo.xml ${OUTDIR}
        cp ${NIPTOUT}/${RUN}_*/*_MISINDEXED_RESULTS.csv ${OUTDIR}
        cp ${NIPTOUT}/${RUN}_*/*_NIPT_RESULTS.csv ${OUTDIR}
        cp ${NIPTOUT}/${RUN}_*/REPORT.Complete.txt ${OUTDIR}
        
    	SUBJECT=$(sed 's//\n/g' ${NIPTRUNS}/${RUN}/SampleSheet.csv  | grep 'Investigator Name' - | cut -d, -f2)
        RESULTS_FILE="results_${SUBJECT}.tgz"

        cd ${OUTDIR}
        tar -czf ${RESULTS_FILE} *
        cd -
        mail -s "Results ${SUBJECT}" -a ${OUTDIR}/${RESULTS_FILE} ${MAILTO} < ${NIPTOUT}/${RUN}_*/REPORT.Complete.txt 
        rm -Rf ${OUTDIR}

	date +'%Y%m%d%H%M%S' > ${NIPTRUNS}/${RUN}/delivery.txt
    fi
done
