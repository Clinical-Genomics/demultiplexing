#!/bin/bash

shopt -s expand_aliases
source ../scripts/demux.functions

TEST_DIR=fixtures

OK() {
    echo "OK"
}

NOK() {
    echo "NOK"
}

# test out basemask creation

echo -n '170531_D00410_0425_AHKL7LBCXY Y101,I8,Y101 '
[[ $(get_basemask ${TEST_DIR}/170531_D00410_0425_AHKL7LBCXY/) == 'Y101,I8,Y101' ]] && echo $(OK) || echo $(NOK)

echo -n '170517_D00456_0219_AHJY2MBCXY Y51,I8,I8 '
[[ $(get_basemask ${TEST_DIR}/170517_D00456_0219_AHJY2MBCXY/) == 'Y51,I8,I8' ]] && echo $(OK) || echo $(NOK)

echo -n '170511_D00456_0216_BHKLC5BCXY Y101,I6nn,Y101 '
[[ $(get_basemask ${TEST_DIR}/170511_D00456_0216_BHKLC5BCXY/) == 'Y101,I6nn,Y101' ]] && echo $(OK) || echo $(NOK)

echo -n '140303_D00410_0050_BH8ETTADXX Y101,I6nn,Y101 '
[[ $(get_basemask ${TEST_DIR}/140303_D00410_0050_BH8ETTADXX/) == 'Y101,I6n,Y101' ]] && echo $(OK) || echo $(NOK)

echo -n '170530_M03284_0060_000000000-B59LF Y301,I8,I8,Y301 '
[[ $(get_basemask ${TEST_DIR}/170530_M03284_0060_000000000-B59LF/) == 'Y301,I8,I8,Y301' ]] && echo $(OK) || echo $(NOK)
