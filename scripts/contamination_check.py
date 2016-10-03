#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from urllib import urlretrieve
from glob import glob

def download_sample_sheet(demux_dir):
    filename = demux_dir + '/SampleSheet.csv'
    run_name = os.path.basename(demux_dir)
    flowcell = run_name.split('_')[-1][1:]
    (dl_filename, headers) = urlretrieve('http://tools.scilifelab.se/samplesheet/{}.csv'.format(flowcell), filename)

def get_sample_sheet(demux_dir):
    sample_sheet = []

    samplesheet_file_name = demux_dir + "/SampleSheet.csv"
    if not os.path.exists(samplesheet_file_name):
        download_sample_sheet(demux_dir)
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

def get_reads(logfile, index, length=0):
    """ Gets the amount of reads for index. If index is smaller than
    listed indeces in logfile, only first hit is returned.

    Args:
        logfile (path): path to log file that holds requested index
        index (str): the index to correlate

    returns (int): reads for index

    """

    if not length:
        length = len(index)

    with open(logfile, 'r') as log:
        for line in log:
            line = line.strip(' \n')
            line = line.split(' ')
            if len(line) > 1 and line[1].startswith(index, 0, length):
                return line
    return ('0', index)

def get_lane(logfilename):
    """ Gets the lane number from the file name

    Args:
        logfilename (string): name of the log file

    Returns (int): lane number

    """
    # try the X syntax
    lane = logfilename.split('.')[0]

    if lane.isdigit():
        return lane

    return re.match(r'L(\d)', logfilename).group(1)

def main(logfile, index):
    """todo: docstring for main.

    args:
        logfile (path): path to log file that holds requested index
        index (str): the index to corrolate

    """

    #import ipdb; ipdb.set_trace()
    # get lane number
    logfilename = os.path.basename(logfile)
    lane = get_lane(logfilename)

    # get fully qualified run dir
    rundir = os.path.dirname(os.path.dirname(logfile))

    # get run name
    runname = os.path.basename(rundir)

    # get samplesheet
    samplesheet = get_sample_sheet(rundir)

    # get the # reads
    reads, found_index = get_reads(logfile, index)

    # get the samples with that lane
    lane_sample = []
    lane_index = []
    for line in samplesheet:
        if line['Lane'] == lane:
            lane_sample.append(line['SampleID'])
            if '_' in line['SampleID']:
                lane_index.append(line['SampleID'].split('_')[1])

    outline = []
    outline.extend(runname.split('_'))
    outline.extend(['LOG', lane, reads, found_index])
    outline.extend([','.join(lane_sample)])
    outline.extend([','.join(lane_index)])

    print(' '.join(outline))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
