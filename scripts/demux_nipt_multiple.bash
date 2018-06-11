#!/bin/bash

SHEETS=( $(find ~/NIPT/ -maxdepth 2 -name SampleSheet.ori) )

while read BATCH; do 
    echo -n $BATCH

    for SHEET in ${SHEETS[@]}; do
        if grep -qs $BATCH $SHEET; then
            RUNDIR=$(dirname $SHEET)
            if [[ ! -e ${RUNDIR}/niptdemuxcomplete.txt ]]; then
                echo "bash demux_nipt.bash ${RUNDIR}"
                if bash demux_nipt.bash ${RUNDIR}; then
                    touch ${RUNDIR}/niptdemuxcomplete.txt
                fi
            fi
        fi
    done

    echo
done < ~/tmp/nipt/outpos.txt 
