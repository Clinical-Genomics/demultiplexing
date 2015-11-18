#!/bin/bash
#   usage:
#      getfastq2.bash <absloute-unaligned-base>
#      Output fastq files will appear in the OUT dir (see below) inder project/flowcell
#      20140227 - made delivered files group writable
#      20140203 - made sure that meta.txt is made from an empty file
#      20140130 - removed R (ori) from output name
#      20131203 - 'Sample_' is removed from output name
# 
UNALIGNBASE=$(echo $1 | awk '{if (substr($0,length($0),1) != "/") {print $0"/"} else {print $0}}')
OUT=/mnt/hds/proj/bioinfo/OUTBOX/
RUN=$(echo ${UNALIGNBASE} | awk 'BEGIN {FS="/"} {print $(NF-1)}')
PLOG=$(ls ${UNALIGNBASE} | grep projectlog)
PROJECTLOG=${UNALIGNBASE}${PLOG}
NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] [${RUN}] Copy to rasta finished >> ${PROJECTLOG}
echo [${NOW}] [${RUN}] running $0
echo $RUN
echo $UNALIGNBASE
DATE=$(echo ${UNALIGNBASE} | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print arr[1]}')
echo $DATE
FC=$(echo ${UNALIGNBASE} | awk 'BEGIN {FS="/"} {split($(NF-1),arr,"_");print substr(arr[4],2,length(arr[4]))}')
echo $FC
UNALIGNDIRS=( $(ls -d ${UNALIGNBASE}Unaligned*/) )
echo ${UNALIGNDIRS[@]}
for UNALIGNDIR in ${UNALIGNDIRS[@]}; do
  echo ${UNALIGNDIR}
  PROJs=$(ls ${UNALIGNDIR}/ | grep Proj)
  for PROJ in ${PROJs[@]};do
    echo ${PROJ}
    mkdir -p ${OUT}${PROJ}
    echo [${NOW}] [${RUN}] mkdir -p ${OUT}${PROJ} >> ${PROJECTLOG}
    samples=$(ls ${UNALIGNDIR}/${PROJ} | grep Sa)
    mkdir -p ${OUT}${PROJ}/${FC}
    chmod g+w ${OUT}${PROJ}/${FC}
    echo "[${NOW}] [${RUN}] chmod g+w ${OUT}${PROJ}/${FC}" >> ${PROJECTLOG}
    for vars in ${samples[@]};do
      NOW=$(date +"%Y%m%d%H%M%S")
      var=$(echo ${vars} | sed 's/Sample_//')
      echo ${UNALIGNDIR}/${PROJ}/${vars}
      echo [${NOW}] [${RUN}] ${UNALIGNDIR}/${PROJ}/${vars} >> ${PROJECTLOG}
      BARCODE=$(ls ${UNALIGNDIR}/${PROJ}/${vars} | grep _L001_R1_001.fastq.gz | awk '{len=split($1,arr,"_");print arr[len-3]}')
  #echo before cat
  #ls -al ${OUT}${PROJ}/${FC}/
      cat ${UNALIGNDIR}/${PROJ}/${vars}/*_L001_R1_* > ${OUT}${PROJ}/${FC}/1_${DATE}_${FC}_${var}_${BARCODE}_1.fastq.gz
      cat ${UNALIGNDIR}/${PROJ}/${vars}/*_L002_R1_* > ${OUT}${PROJ}/${FC}/2_${DATE}_${FC}_${var}_${BARCODE}_1.fastq.gz
      cat ${UNALIGNDIR}/${PROJ}/${vars}/*_L001_R2_* > ${OUT}${PROJ}/${FC}/1_${DATE}_${FC}_${var}_${BARCODE}_2.fastq.gz
      cat ${UNALIGNDIR}/${PROJ}/${vars}/*_L002_R2_* > ${OUT}${PROJ}/${FC}/2_${DATE}_${FC}_${var}_${BARCODE}_2.fastq.gz
  #echo after cat
  #ls -al ${OUT}${PROJ}/${FC}/
      echo "[${NOW}] [${RUN}] cat ${UNALIGNDIR}/${PROJ}/${vars}/*_L001_R1_* > ${OUT}${PROJ}/${FC}/1_${DATE}_${FC}_${var}_${BARCODE}_1.fastq.gz" >> ${PROJECTLOG}
      echo "[${NOW}] [${RUN}] cat ${UNALIGNDIR}/${PROJ}/${vars}/*_L002_R1_* > ${OUT}${PROJ}/${FC}/2_${DATE}_${FC}_${var}_${BARCODE}_1.fastq.gz" >> ${PROJECTLOG}
      echo "[${NOW}] [${RUN}] cat ${UNALIGNDIR}/${PROJ}/${vars}/*_L001_R2_* > ${OUT}${PROJ}/${FC}/1_${DATE}_${FC}_${var}_${BARCODE}_2.fastq.gz" >> ${PROJECTLOG}
      echo "[${NOW}] [${RUN}] cat ${UNALIGNDIR}/${PROJ}/${vars}/*_L002_R2_* > ${OUT}${PROJ}/${FC}/2_${DATE}_${FC}_${var}_${BARCODE}_2.fastq.gz" >> ${PROJECTLOG}
      chmod g+w ${OUT}${PROJ}/${FC}/1_${DATE}_${FC}_${var}_${BARCODE}_1.fastq.gz
      chmod g+w ${OUT}${PROJ}/${FC}/2_${DATE}_${FC}_${var}_${BARCODE}_1.fastq.gz
      chmod g+w ${OUT}${PROJ}/${FC}/1_${DATE}_${FC}_${var}_${BARCODE}_2.fastq.gz
      chmod g+w ${OUT}${PROJ}/${FC}/2_${DATE}_${FC}_${var}_${BARCODE}_2.fastq.gz
      echo [${NOW}] [${RUN}] chmod g+w ${OUT}${PROJ}/${FC}/1_${DATE}_${FC}_${var}_${BARCODE}_1.fastq.gz >> ${PROJECTLOG}
      echo [${NOW}] [${RUN}] chmod g+w ${OUT}${PROJ}/${FC}/2_${DATE}_${FC}_${var}_${BARCODE}_1.fastq.gz >> ${PROJECTLOG}
      echo [${NOW}] [${RUN}] chmod g+w ${OUT}${PROJ}/${FC}/1_${DATE}_${FC}_${var}_${BARCODE}_2.fastq.gz >> ${PROJECTLOG}
      echo [${NOW}] [${RUN}] chmod g+w ${OUT}${PROJ}/${FC}/2_${DATE}_${FC}_${var}_${BARCODE}_2.fastq.gz >> ${PROJECTLOG}
  #echo end of loop
  #ls -al ${OUT}${PROJ}/${FC}/
    done
    prj=$(echo ${PROJ} | sed 's/Project_//')
    cp /mnt/hds/proj/bioinfo/DEMUX/${RUN}/stats-${prj}-${FC}.txt ${OUT}${PROJ}/${FC}/
    echo [${NOW}] [${RUN}] cp /mnt/hds/proj/bioinfo/DEMUX/${RUN}/stats-${prj}-${FC}.txt ${OUT}${PROJ}/${FC}/ >> ${PROJECTLOG}
    echo "" > ${OUT}${PROJ}/${FC}/meta-${prj}-${FC}.txt
    r1s=$(ls ${OUT}${PROJ}/${FC}/ | grep _1.fastq.gz)
    echo [${NOW}] [${RUN}] DELIVERY to OUTBOX finished >> ${PROJECTLOG}
    cp ${PROJECTLOG} ${OUT}${PROJ}/${FC}/
  #ls -al ${OUT}${PROJ}/${FC}/
    for r1 in ${r1s[@]};do
      r2=$(echo $r1 | sed 's/_1.fastq.gz/_2.fastq.gz/')
      bc=$(echo $r1 | awk 'BEGIN {FS="_"} {print $(NF-1)}' | sed 's/index//')
      lane=$(echo $r1 | awk 'BEGIN {FS="_"} {print $1}')
      fc=$(echo $r1 | awk 'BEGIN {FS="_"} {print $3}')
      sample=$(echo $r1 | awk 'BEGIN {FS="_"} {print $4"_"$5"_"$6"_"$7"_"$8}' | sed 's/_1.fastq.gz//' | sed "s/_${bc}//")
      echo $sample $fc $lane $bc $r1 $r2 | awk 'BEGIN {OFS="\t"} {print $1,$2,$3,$4,$5,$6}' >> ${OUT}${PROJ}/${FC}/meta-${prj}-${FC}.txt
      bash /mnt/hds/proj/bioinfo/git/rikard/analysis/scripts/prepare_sample_for_mip.bash $sample ${OUT}${PROJ}/${FC}/${PLOG}
    done
    chmod g+w ${OUT}${PROJ}/${FC}/meta-${prj}-${FC}.txt
    chmod g+w ${OUT}${PROJ}/${FC}/stats-${prj}-${FC}.txt
    echo [${NOW}] [${RUN}] chmod g+w ${OUT}${PROJ}/${FC}/meta-${prj}-${FC}.txt >> ${PROJECTLOG}
    echo [${NOW}] [${RUN}] chmod g+w ${OUT}${PROJ}/${FC}/stats-${prj}-${FC}.txt >> ${PROJECTLOG}
  #    the two entries above will not be copied to the log proj/fc/
  
  done
done
NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] [${RUN}] DELIVERY to OUTBOX finished >> ${UNALIGNBASE}delivery.txt
ls -al ${OUT}${PROJ}/${FC}/

