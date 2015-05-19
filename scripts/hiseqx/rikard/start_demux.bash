#!/bin/bash
NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] starting overall process
lanes=(1 2 3 4 5 6 7 8)
for lane in ${lanes[@]}; do
  sed "s/NUMBER/${lane}/g" template.batch > lane${lane}.batch
  NOW=$(date +"%Y%m%d%H%M%S")
  echo [${NOW}] starting lane${lane}
  sbatch lane${lane}.batch
done
NOW=$(date +"%Y%m%d%H%M%S")
echo [${NOW}] everything started
