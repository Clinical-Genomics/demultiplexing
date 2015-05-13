#!/bin/bash
# script to send run results

##########
# PARAMS #
##########

NIPTRUNS=/home/clinical/NIPT/
NIPTOUT=/srv/nipt_analysis_output/
MAILTO=kenny.billiau@scilifelab.se
CC=emma.sernstad@scilifelab.se

#######
# RUN #
#######

for RUN in $(ls ${NIPTRUNS}); do
    NOW=$(date +"%Y%m%d%H%M%S")
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
        
        cd ${OUTDIR}
        tar -czf results_${RUN}.tgz *
        cd -
        mail -s "Results NIPT ${RUN}" -a ${OUTDIR}/results_${RUN}.tgz ${MAILTO} -c ${CC} < ${NIPTOUT}/${RUN}_*/REPORT.Complete.txt 
        rm -Rf ${OUTDIR}

	date +'%Y%m%d%H%M%S' > ${NIPTRUNS}/${RUN}/delivery.txt
    fi
done
