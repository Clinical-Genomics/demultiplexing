#!/bin/bash


INDIR=/mnt/hds2/proj/bioinfo/Runs/150227_ST-E00214_0020_AH2VK3CCXX
TILES=('11 12' '21 22')

for LANE in {1..8}; do
    echo $LANE
    for TILE in ${TILES[@]}; do
        tile_size_1=$(du -s ${INDIR}/Data/Intensities/BaseCalls/L00${LANE}/*/s_${LANE}_${TILE}* | awk '{s+=$1}END{print s}')
        tile_size_2=$(du -s ${INDIR}/Data/Intensities/BaseCalls/L00${LANE}/s_${LANE}_${TILE}* | awk '{s+=$1}END{print s}')
        echo $((tile_size_1 + tile_size_2))
    done
done
