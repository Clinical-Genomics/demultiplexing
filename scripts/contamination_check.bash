#!/bin/bash

DEMUX=${1?'Please provide a DEMUX run dir'}
EMAIL=$2

cleanup() {
    if [[ -e $OUTPUT ]]; then
        rm ${OUTPUT}
    fi
}
trap "cleanup" EXIT

OUTPUT=$(mktemp)

# 2500
for LOG in ${DEMUX}/LOG/L*.txt; do
    python contamination_check.py ${LOG} CTTGTAAT 2> /dev/null >> $OUTPUT
#    python contamination_check.py ${LOG} CTTGTA   2> /dev/null
#    python contamination_check.py ${LOG} TTGTAA   2> /dev/null
#    python contamination_check.py ${LOG} TGTAAT   2> /dev/null
done

# X
for LOG in *_ST*/LOG/?.index.stats.txt; do
    python contamination_check.py $LOG CTTGTAAT 2> /dev/null >> $OUTPUT
done

if [[ -n $EMAIL ]]; then
    mail -s "Data for $DEMUX" $EMAIL < $OUTPUT
fi
cat $OUTPUT
exit 0
