#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division

import xml.etree.ElementTree as et
import sys
import glob

__version__ = '3.18.1'

def xpathsum(tree, xpath):
    """Sums all numbers found at these xpath nodes

    Args:
        tree (an elementTree): parsed XML as an elementTree
        xpath (str): an xpath the XML nodes

    Returns (int): the sum of all nodes

    """
    numbers = tree.findall(xpath)
    return sum([ int(number.text) for number in numbers ])

def get_summary(tree):
    """Calculates following statistics from the provided elementTree:
    * pf clusters
    * pf yield
    * pf Q30
    * raw Q30
    * pf Q Score

    Args:
        tree (an elementTree): parsed XML as an elementTree

    Returns (dict): with following keys: pf_clusters, pf_yield, pf_q30, raw_q30, pf_qscore_sum, pf_qscore

    """
    #raw_clusters = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Raw/ClusterCount")
    pf_clusters = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/ClusterCount")

    pf_yield = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read/Yield")
    #raw_yield = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Raw/Read/Yield")
    #pf_clusters_pc = pf_yield / raw_yield

    pf_q30 = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read/YieldQ30")
    raw_q30 = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Raw/Read/YieldQ30")
    #pf_q30_bases_pc = pf_q30 / pf_yield

    pf_qscore_sum = xpathsum(tree, ".//Project[@name='all']/Sample[@name='all']/Barcode[@name='all']//Pf/Read/QualityScoreSum")
    pf_qscore = pf_qscore_sum / pf_yield

    return {
        #'raw_clusters': raw_clusters,
        #'raw_yield': raw_yield,
        #'pf_clusters_pc': pf_clusters_pc,
        #'pf_q30_bases_pc': pf_q30_bases_pc,
        'pf_clusters': pf_clusters,
        'pf_yield': pf_yield,
        'pf_q30': pf_q30,
        'raw_q30': raw_q30,
        'pf_qscore_sum': pf_qscore_sum,
        'pf_qscore': pf_qscore
    }

def get_samplesheet(rundir, file_name='SampleSheet.csv', delim=','):
    """Reads in and parses a samplesheet. The samplesheet is found in the provided rundir.
    Lines starting with #, [ and blank will be skipped.
    First line will be taken as the header.

    Args:
        rundir (path): FQ path of rundir
        delim (str): the samplesheet delimiter

    Returns (list of dicts): 
        Keys are the header, values the lines.

    """
    with open(rundir + '/' + file_name) as sample_sheet:
        lines = [ line for line in sample_sheet.readlines() if not line.startswith(('#', '[')) and len(line) ] # skip comments and special headers
        lines = [ line.strip().split(delim) for line in lines ] # read lines

        header = lines[0]

        return [ dict(zip(header, line)) for line in lines[1:] ]

def get_lanes(sample_sheet):
    """Get the lanes from the SampleSheet

    Args:
        sample_sheet (list of dicts): a samplesheet with each line a dict. The keys are the header, the values the split line

    Returns:
        a list of lane numbers

    """
    return [ line['Lane'] for line in sample_sheet ] # remove headers

def main(argv):
    """Takes a DEMUX dir and calculates statistics for the run.

    Args:
        argv[0] (str): the DEMUX dir

    """

    sample_sheet = get_samplesheet(argv[0])
    lanes = get_lanes(sample_sheet)

    # create a { 1: [], 2: [], ... } structure
    summaries = dict(zip(lanes, [ [] for t in xrange(len(lanes))])) # init ;)

    # get all the stats numbers
    for lane in lanes:
        stats_files = glob.glob('%s/l%st??/Stats/ConversionStats.xml' % (argv[0], lane))

        if len(stats_files) == 0:
            exit("No stats file found for lane {}".format(lane))

        for i, f in enumerate(stats_files):
            tree = et.parse(f)
            summaries[ lane ].append(get_summary(tree))
    
    # sum the numbers over a lane
    # create a { 1: {'raw_clusters': 0, ... } } structure
    total_lane_summary = {}
    for line in sample_sheet:
        total_lane_summary[ line['Lane'] ] = {
            #'raw_clusters': 0,
            #'raw_yield': 0,
            #'pf_clusters_pc': 0,
            #'pf_q30_bases_pc': 0,
            'pf_clusters': 0,
            'pf_yield': 0,
            'pf_q30': 0,
            'raw_q30': 0,
            'pf_qscore_sum': 0,
            'pf_qscore': 0,
            'flowcell': line['FCID'],
            'samplename': line['SampleID']
        }

    for lane, summary in summaries.items():
        for summary_quart in summary:
            for key, stat in summary_quart.items():
                total_lane_summary[lane][ key ] += stat

    # print me a pretty report
    print('\t'.join(('Sample', 'Flowcell', 'Lane', 'PF clusters', 'YieldMB', 'Q30', 'MeanQScore')))
    for lane, summary in total_lane_summary.items():
        print('\t'.join( [
            summary['samplename'],
            summary['flowcell'],
            lane,
            str(summary['pf_clusters']),
            str(round(summary['pf_yield'] / 1000000, 0)),
            str(round(summary['pf_q30'] / summary['pf_yield'] * 100, 2)),
            str(round(summary['pf_qscore_sum'] / summary['pf_yield'], 2))
        ]))

if __name__ == '__main__':
    main(sys.argv[1:])
