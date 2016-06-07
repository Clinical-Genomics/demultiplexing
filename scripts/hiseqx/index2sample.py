#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from glob import glob

def get_sample_sheet(demux_dir):
    sample_sheet = []
    samplesheet_file_name = glob("{demux_dir}/SampleSheet.csv".format(demux_dir=demux_dir))[0]
    with open(samplesheet_file_name, 'r') as samplesheet_fh:
        lines = [ line.strip().split(',') for line in samplesheet_fh.readlines() ]
        header = []
        for line in lines:
            # skip headers
            if line[0].startswith('['): continue
            if line[2] == 'SampleID':
                header = line
                continue

            entry = dict(zip(header, line))
            sample_sheet.append(entry)

    return sample_sheet

def main(logfile, index):
    """TODO: Docstring for main.

    Args:
        logfile (path): path to log file that holds requested index
        index (str): the index to corrolate

    """
    # get lane number
    logfilename = os.path.basename(logfile)
    lane = logfilename.split('.')[0]
    # get run dir
    rundir = os.path.dirname(os.path.dirname(logfile))
    # get samplesheet
    samplesheet = get_sample_sheet(rundir)

    # get the samples with that lane
    lane_sample = []
    lane_index = []
    for line in samplesheet:
        if line['Lane'] == lane:
            lane_sample.append(line['SampleID'])
            if '_' in line['SampleID']:
                lane_index.append(line['SampleID'].split('_')[1])

    print(','.join(lane_index))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
